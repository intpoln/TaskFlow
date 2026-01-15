"""Репозиторий для работы с пользователями.

Содержит методы для поиска и получения пользователей.
"""

from sqlalchemy import or_, select

from src.core.exceptions import NotFoundError
from src.models import UserOrm
from src.repositories.base import BaseRepository
from src.schemas.users import User


class UserRepository(BaseRepository[UserOrm]):
    """Репозиторий пользователей.

    Расширяет BaseRepository методами для проверки
    существования пользователей и поиска по email/username.
    """

    model = UserOrm

    async def user_exists(self, email: str, username: str) -> UserOrm | None:
        """Проверяет существование пользователя с указанным email или username.

        Используется при регистрации для предотвращения дубликатов.

        Args:
            email: Email для проверки.
            username: Username для проверки.

        Returns:
            Найденный пользователь или None.
        """
        query = select(self.model).where(
            or_(self.model.email == email, self.model.username == username)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Получает пользователя по ID и возвращает Pydantic схему.

        Args:
            user_id: ID пользователя.

        Returns:
            Пользователь в виде Pydantic схемы.

        Raises:
            NotFoundError: Пользователь не найден.
        """
        query = select(self.model).filter_by(id=user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError(f"Пользователь с id {user_id} не найден")
        return User.model_validate(user)
