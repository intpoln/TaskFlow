from fastapi import Request
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select

from src.config import settings
from src.database import async_session_maker
from src.models.users import UserOrm as User
from src.models.categories import CategoryOrm as Category
from src.services.auth import AuthService


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get('username')
        password = form.get('password')

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
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get('access_token')

        if not token:
            return False
        payload = AuthService.decode_access_token(token)
        return payload is not None

authentication_backend = AdminAuth(secret_key=settings.JWT_SECRET_KEY)


class UserAdmin(ModelView, model=User):
    column_exclude_list = [User.hashed_password]
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    name = 'User'
    name_plural = 'Users'
    column_searchable_list = column_sortable_list = [User.email, User.id, User.username,
                                                     User.created_at, User.telegram_username]


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.title]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = 'Category'
    name_plural = 'Categories'
    column_searchable_list = column_sortable_list = [Category.id, Category.title,]
