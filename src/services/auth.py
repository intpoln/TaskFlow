"""Сервис аутентификации.

Содержит бизнес-логику регистрации, авторизации и работы с токенами.
"""

import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import httpx
from jose import jwt
from jose.exceptions import JWTError

from src.config import settings
from src.core.exceptions import (
    ConflictError,
    ExternalServiceError,
    ForbiddenError,
    NotAuthorizedError,
    NotFoundError,
)
from src.init import redis_manager
from src.schemas.users import User, UserLogin, UserRegister
from src.services.base import BaseService
from src.utils.oauth import get_google_jwks


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

    async def register(self, data: UserRegister) -> User:
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
        existing_user = await self.db.users.user_exists(email=data.email)

        if existing_user:
            raise ConflictError("Пользователь с таким email уже существует")

        hashed_password = self.hash_password(data.password)
        user = await self.db.users.create(
            {
                "email": data.email,
                "username": data.username,
                "hashed_password": hashed_password,
            }
        )
        await self.db.commit()
        return user

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
        try:
            user = await self.db.users.get_filtered_one(email=data.email)
        except NotFoundError:
            raise ForbiddenError("Неверный email или пароль")

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
        to_encode |= {"exp": expire, "type": "access", "jti": str(uuid4())}
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
        except JWTError:
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
        to_encode |= {"exp": expire, "type": "refresh", "jti": str(uuid4())}
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
        except JWTError:
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

    async def generate_google_oauth_redirect_uri(self) -> str:
        """Генерирует URL для редиректа на Google OAuth.

        Создаёт случайный state, сохраняет его в Redis
        и формирует URL авторизации Google.

        Returns:
            URL для редиректа на страницу авторизации Google.

        Raises:
            RedisConnectionError: При ошибке подключения к Redis.
        """
        state = secrets.token_urlsafe(32)
        await redis_manager.set_oauth_state(state)

        query_params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_CALLBACK_URI,
            "response_type": "code",
            "scope": " ".join(["openid", "email", "profile"]),
            "state": state,
        }

        query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
        base_url = settings.GOOGLE_OAUTH_AUTHORIZE_URI
        return f"{base_url}?{query_string}"

    async def authenticate_google_user(
        self, code: str, state: str, fingerprint: str | None = None
    ) -> dict:
        """Аутентифицирует пользователя через Google OAuth.

        Полный flow: проверка state → обмен code на токен →
        валидация id_token → регистрация/поиск пользователя → выдача токенов.

        Args:
            code: Authorization code от Google.
            state: State для защиты от CSRF.
            fingerprint: User-Agent для fingerprint токена.

        Returns:
            Словарь с access_token и refresh_token.

        Raises:
            ForbiddenError: Невалидный state или данные от Google.
            ExternalServiceError: Ошибка при обращении к Google API.
            NotAuthorizedError: Невалидный id_token.
        """
        await self._verify_oauth_state(state)

        id_token = await self._exchange_code_for_id_token(code)

        token_payload = await self._decode_google_id_token(id_token)

        user = await self._find_or_create_google_user(
            email=token_payload["email"],
            username=token_payload.get("name"),
            google_id=token_payload["sub"],
        )

        return self._generate_tokens(user.id, fingerprint)

    async def _verify_oauth_state(self, state: str) -> None:
        """Проверяет OAuth state (one-time use).

        Args:
            state: State из callback URL.

        Raises:
            ForbiddenError: State невалиден или истёк.
        """
        is_valid = await redis_manager.verify_oauth_state(state)
        if not is_valid:
            raise ForbiddenError("Невалидный или истёкший state. Попробуйте снова.")

    async def _exchange_code_for_id_token(self, code: str) -> str:
        """Обменивает authorization code на id_token.

        Args:
            code: Authorization code от Google.

        Returns:
            JWT id_token от Google.

        Raises:
            ExternalServiceError: Ошибка при запросе к Google.
            ForbiddenError: Ответ не содержит id_token.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.GOOGLE_OAUTH_GET_TOKEN_URI,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": settings.GOOGLE_CALLBACK_URI,
                    },
                    timeout=15,
                )
        except httpx.RequestError:
            raise ExternalServiceError("Не удалось подключиться к Google OAuth")

        if response.status_code != 200:
            raise ExternalServiceError("Ошибка авторизации Google. Попробуйте позже.")

        data = response.json()
        id_token = data.get("id_token")

        if not id_token:
            raise ForbiddenError("Google не вернул id_token")

        return id_token

    async def _decode_google_id_token(self, id_token: str) -> dict:
        """Декодирует и валидирует Google id_token.

        Проверяет подпись через JWK, issuer, audience и срок действия.

        Args:
            id_token: JWT токен от Google.

        Returns:
            Payload токена (email, sub, name и т.д.).

        Raises:
            NotAuthorizedError: Токен невалиден или не прошёл проверку.
            ExternalServiceError: Не удалось получить JWK для проверки.
        """
        try:
            jwks = await get_google_jwks()

            payload = jwt.decode(
                id_token,
                jwks,
                algorithms=["RS256"],
                audience=settings.GOOGLE_CLIENT_ID,
                issuer=settings.GOOGLE_ISSUER,
                options={"verify_at_hash": False},
            )
            return payload

        except JWTError as ex:
            raise NotAuthorizedError(f"Невалидный токен Google: {str(ex)}")

    async def _find_or_create_google_user(self, email: str, username: str, google_id: str):
        """Находит или создаёт пользователя по данным Google.

        Логика:
        1. Если есть пользователь с таким email, но без google_id — привязываем.
        2. Если нет пользователя — создаём нового.
        3. Если уже привязан — просто возвращаем.

        Args:
            email: Email от Google.
            username: Имя от Google.
            google_id: Google sub (уникальный ID).

        Returns:
            ORM модель пользователя.
        """
        existing_user = await self.db.users.user_exists(email=email)

        if existing_user:
            if not existing_user.google_id:
                user = await self.db.users.update(
                    id=existing_user.id,
                    data={"google_id": google_id},
                )
                await self.db.commit()
                return user
            return existing_user

        user = await self.db.users.create(
            {
                "email": email,
                "username": username,
                "google_id": google_id,
            }
        )
        await self.db.commit()
        return user
