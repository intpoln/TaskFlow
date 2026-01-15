from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from src.config import settings
from src.core.exceptions import ConflictError, ForbiddenError, NotAuthorizedError, NotFoundError
from src.schemas.users import User, UserLogin, UserRegister
from src.services.base import BaseService


class AuthService(BaseService):
    def _generate_tokens(self, user_id: int, fingerprint: str | None = None) -> dict:
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
        user = await self.db.users.get_filtered_one(email=data.email)

        if not user or not self.verify_password(data.password, user.hashed_password):
            raise ForbiddenError("Неверный email или пароль")

        return self._generate_tokens(user.id, fingerprint)

    async def refresh(self, refresh_token: str | None, fingerprint: str | None = None) -> dict:
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
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire, "type": "access"}
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITM)

    @staticmethod
    def decode_access_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITM])
            if payload.get("type") != "access":
                return None
            return payload
        except InvalidTokenError:
            return None

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode |= {"exp": expire, "type": "refresh"}
        return jwt.encode(
            to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITM
        )

    @staticmethod
    def decode_refresh_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITM]
            )
            if payload.get("type") != "refresh":
                return None
            return payload
        except InvalidTokenError:
            return None

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    async def get_user_by_token(self, access_token: str) -> User | None:
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
        if not user.is_superuser:
            raise ForbiddenError("Недостаточно прав")
        return True
