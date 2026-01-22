"""Pydantic схемы для пользователей.

Содержит схемы для регистрации, авторизации и отображения пользователей.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRegister(BaseModel):
    """Схема регистрации нового пользователя.

    Attributes:
        email: Email адрес пользователя.
        password: Пароль в открытом виде.
        username: Желаемый логин.
    """

    email: EmailStr
    password: str
    username: str


class UserLogin(BaseModel):
    """Схема авторизации пользователя.

    Attributes:
        email: Email адрес для входа.
        password: Пароль пользователя.
    """

    email: EmailStr
    password: str


class UserAdd(BaseModel):
    """Внутренняя схема для создания пользователя в БД.

    Используется репозиторием, содержит хешированный пароль.

    Attributes:
        email: Email адрес.
        hashed_password: Хеш пароля (bcrypt).
        username: Логин пользователя.
    """

    email: EmailStr
    hashed_password: str
    username: str


class User(BaseModel):
    """Схема пользователя для API ответов.

    Не содержит чувствительных данных (пароль, is_superuser).

    Attributes:
        id: Уникальный идентификатор.
        email: Email адрес.
        username: Логин пользователя.
        created_at: Дата регистрации.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    created_at: datetime