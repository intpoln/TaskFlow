"""ORM модель пользователя.

Содержит модель UserOrm для хранения данных пользователей.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.database import Base


class UserOrm(Base):
    """Модель пользователя в базе данных.

    Хранит данные аккаунта: email, логин, пароль (хеш),
    а также опциональную интеграцию с Telegram.

    Attributes:
        id: Уникальный идентификатор пользователя.
        email: Email адрес (уникальный).
        hashed_password: Хеш пароля (bcrypt).
        username: Логин пользователя (уникальный).
        created_at: Дата и время регистрации.
        is_superuser: Флаг суперпользователя (админ).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    hashed_password: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(String(30), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    is_superuser: Mapped[bool] = mapped_column(default=False)
