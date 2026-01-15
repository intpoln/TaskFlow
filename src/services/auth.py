"""Сервис аутентификации.

Содержит бизнес-логику регистрации, авторизации и работы с токенами.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from src.config import settings
from src.core.exceptions import ConflictError, ForbiddenError, NotAuthorizedError, NotFoundError
from src.schemas.users import User, UserLogin, UserRegister
from src.services.base import BaseService


class AuthService(BaseService):
    """Сервис аутентификации и авторизации.

    Предоставляет методы для:
    - Регистрации новых пользователей
    - Создания и обновления JWT токенов
    - Проверки прав доступа
    """

    def _generate_tokens(self, user_id: int, fingerprint: str | None = None) -> dict:
        """Генерирует пару access и refresh токенов.

        Args:
            user_id: ID пользователя для включения в payload.
            fingerprint: Отпечаток браузера (User-Agent) для защиты refresh токена.

        Returns:
            Словарь с access_token и refresh_token.
        """
        access_token = self.create_access_token({"user_id": user_id})

        refresh_data = {"user_id": user_id}
        if fingerprint:
            refresh_data["fingerprint"] = fingerprint

        refresh_token = self.create_refresh_token(refresh_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def register(self, data: UserRegister) -> dict:
        """Регистрирует нового пользователя.

        Проверяет уникальность email и username,
        хеширует пароль и сохраняет пользователя в БД.

        Args:
            data: Данные для регистрации.

        Returns:
            Словарь с результатом операции.

        Raises:
            ConflictError: Пользователь с таким email или username уже существует.
        """
        existing_user = await self.db.users.user_exists(email=data.email, username=data.username)

        if existing_user:
            if existing_user.email == data.email:
                raise ConflictError("Пользователь с таким email уже существует")
            raise ConflictError("Пользователь с таким username уже существует")

        hashed_password = self.hash_password(data.password)
        await self.db.users.create(
            {
                "email": data.email,
                "username": data.username,
                "hashed_password": hashed_password,
            }
        )
        await self.db.commit()
        return {"status": True, "message": f"Пользователь {data.username} успешно зарегистрирован!"}

    async def create_tokens(self, data: UserLogin, fingerprint: str | None = None) -> dict:
        """Создаёт токены при успешной авторизации.

        Args:
            data: Данные для входа (email, password).
            fingerprint: Отпечаток браузера для refresh токена.

        Returns:
            Словарь с access_token и refresh_token.

        Raises:
            ForbiddenError: Неверный email или пароль.
        """
        user = await self.db.users.get_filtered_one(email=data.email)

        if not user or not self.verify_password(data.password, user.hashed_password):
            raise ForbiddenError("Неверный email или пароль")

        return self._generate_tokens(user.id, fingerprint)

    async def refresh(self, refresh_token: str | None, fingerprint: str | None = None) -> dict:
        """Обновляет токены по refresh токену.

        Проверяет валидность refresh токена и fingerprint,
        генерирует новую пару токенов (token rotation).

        Args:
            refresh_token: Текущий refresh токен.
            fingerprint: Отпечаток браузера для верификации.

        Returns:
            Словарь с новыми access_token и refresh_token.

        Raises:
            NotAuthorizedError: Токен истёк, невалиден или fingerprint не совпадает.
        """
        payload = self.decode_refresh_token(refresh_token)
        if not payload:
            raise NotAuthorizedError("Refresh токен истёк, авторизуйтесь заново")

        token_fingerprint = payload.get("fingerprint")
        if token_fingerprint and token_fingerprint != fingerprint:
            raise NotAuthorizedError("Подозрительная активность, авторизуйтесь заново")

        user_id = payload.get("user_id")
        user = await self.db.users.get_by_id(user_id)
        if not user:
            raise NotAuthorizedError("Пользователь не найден")

        return self._generate_tokens(user.id, fingerprint)

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Создаёт JWT access токен.

        Args:
            data: Данные для включения в payload (обычно user_id).

        Returns:
            Закодированный JWT токен.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire, "type": "access"}
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> dict | None:
        """Декодирует и проверяет access токен.

        Args:
            token: JWT access токен.

        Returns:
            Payload токена или None при ошибке.
        """
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "access":
                return None
            return payload
        except InvalidTokenError:
            return None

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Создаёт JWT refresh токен.

        Args:
            data: Данные для payload (user_id, fingerprint).

        Returns:
            Закодированный JWT токен.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode |= {"exp": expire, "type": "refresh"}
        return jwt.encode(
            to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode_refresh_token(token: str) -> dict | None:
        """Декодирует и проверяет refresh токен.

        Args:
            token: JWT refresh токен.

        Returns:
            Payload токена или None при ошибке.
        """
        try:
            payload = jwt.decode(
                token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "refresh":
                return None
            return payload
        except InvalidTokenError:
            return None

    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширует пароль с помощью bcrypt.

        Args:
            password: Пароль в открытом виде.

        Returns:
            Хеш пароля.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля хешу.

        Args:
            password: Пароль для проверки.
            hashed_password: Хеш из БД.

        Returns:
            True если пароль верный.
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    async def get_user_by_token(self, access_token: str) -> User | None:
        """Получает пользователя по access токену.

        Используется для аутентификации запросов.

        Args:
            access_token: JWT access токен из cookie.

        Returns:
            Пользователь (Pydantic схема).

        Raises:
            NotAuthorizedError: Токен отсутствует, невалиден или истёк.
            NotFoundError: Пользователь не найден в БД.
        """
        if not access_token:
            raise NotAuthorizedError("Токен отсутствует")

        decoded_token = self.decode_access_token(access_token)
        if not decoded_token:
            raise NotAuthorizedError("Невалидный или истёкший токен")

        user_id = decoded_token.get("user_id")
        if not user_id:
            raise NotAuthorizedError("Невалидный токен")

        user = await self.db.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")

        return user

    async def verify_superuser(self, user: User) -> bool:
        """Проверяет права суперпользователя.

        Args:
            user: Пользователь для проверки.

        Returns:
            True если пользователь является суперпользователем.

        Raises:
            ForbiddenError: Недостаточно прав.
        """
        if not user.is_superuser:
            raise ForbiddenError("Недостаточно прав")
        return True
