"""Репозиторий для работы с проектами.

Содержит методы для получения проектов пользователя.
"""

from sqlalchemy import select

from src.core.exceptions import NotFoundError
from src.models import ProjectOrm
from src.repositories.base import BaseRepository
from src.schemas.projects import Project


class ProjectRepository(BaseRepository[ProjectOrm]):
    """Репозиторий проектов пользователя.

    Расширяет BaseRepository методами для работы
    с проектами конкретного пользователя.
    """

    model = ProjectOrm

    async def get_user_project(self, project_id: int, user_id: int) -> Project:
        """Получает проект пользователя по ID.

        Проверяет что проект принадлежит указанному пользователю.

        Args:
            project_id: ID проекта.
            user_id: ID владельца.

        Returns:
            Найденный проект.

        Raises:
            NotFoundError: Проект не найден или принадлежит другому пользователю.
        """
        query = select(ProjectOrm).filter_by(id=project_id, owner_id=user_id)
        result = await self.session.execute(query)
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundError(f"Проект с id {project_id} не найден")
        return project
