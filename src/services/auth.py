from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from src.config import settings


class AuthService:

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire, 'type': 'access'}
        return jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITM
        )

    def decode_access_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITM])
            if payload.get('type') != 'access':
                return None
            return payload
        except InvalidTokenError:
            return None

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode |= {"exp": expire, "type": "refresh"}
        return jwt.encode(
            to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITM
        )

    def decode_refresh_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITM])
            if payload.get('type') != 'refresh':
                return None
            return payload
        except InvalidTokenError:
            return None

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
