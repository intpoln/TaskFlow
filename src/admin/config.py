"""Конфигурация административной панели SQLAdmin.

Содержит настройки аутентификации и представления моделей
для административного интерфейса.
"""

from fastapi import Request
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select

from src.config import settings
from src.database import async_session_maker
from src.models.categories import CategoryOrm as Category
from src.models.users import UserOrm as User
from src.services.auth import AuthService


class AdminAuth(AuthenticationBackend):
    """Бэкенд аутентификации для административной панели.

    Реализует проверку учётных данных суперпользователей
    и управление сессиями через JWT токены в cookies.
    """

    async def login(self, request: Request) -> bool:
        """Аутентифицирует администратора.

        Проверяет username/password и флаг is_superuser.
        При успехе сохраняет access_token в сессию.

        Args:
            request: HTTP запрос с формой авторизации.

        Returns:
            True при успешной аутентификации, False иначе.
        """
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        async with async_session_maker() as db:
            query = select(User).filter_by(username=username)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

        if not user:
            return False

        if not AuthService.verify_password(password, user.hashed_password):
            return False

        if not user.is_superuser:
            return False

        access_token = AuthService.create_access_token({"user_id": user.id})
        request.session.update({"access_token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        """Выходит из административной панели.

        Очищает сессию пользователя.

        Args:
            request: HTTP запрос.

        Returns:
            True при успешном выходе.
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Проверяет аутентификацию текущего запроса.

        Валидирует access_token из сессии.

        Args:
            request: HTTP запрос.

        Returns:
            True если пользователь аутентифицирован.
        """
        token = request.session.get("access_token")

        if not token:
            return False
        payload = AuthService.decode_access_token(token)
        return payload is not None


authentication_backend = AdminAuth(secret_key=settings.JWT_SECRET_KEY)


class UserAdmin(ModelView, model=User):
    """Административное представление модели User.

    Только просмотр пользователей, без возможности
    создания, редактирования или удаления.

    Attributes:
        column_exclude_list: Скрытые поля (hashed_password).
        can_create: Запрет создания.
        can_edit: Запрет редактирования.
        can_delete: Запрет удаления.
    """

    column_exclude_list = [User.hashed_password]
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    name = "User"
    name_plural = "Users"
    column_searchable_list = column_sortable_list = [
        User.email,
        User.id,
        User.username,
        User.created_at,
        User.telegram_username,
    ]


class CategoryAdmin(ModelView, model=Category):
    """Административное представление модели Category.

    Полный CRUD для управления категориями задач.

    Attributes:
        column_list: Отображаемые колонки.
        can_create: Разрешено создание.
        can_edit: Разрешено редактирование.
        can_delete: Разрешено удаление.
    """

    column_list = [Category.id, Category.title]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Category"
    name_plural = "Categories"
    column_searchable_list = column_sortable_list = [
        Category.id,
        Category.title,
    ]
