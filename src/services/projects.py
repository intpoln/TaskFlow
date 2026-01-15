"""Сервис для работы с проектами.

Содержит бизнес-логику управления проектами пользователей.
"""

from src.core.exceptions import ConflictError, NotFoundError
from src.schemas.projects import Project, ProjectPUT, ProjectRequest, ProjectUpdate
from src.services.base import BaseService


class ProjectService(BaseService):
    """Сервис управления проектами.

    Предоставляет методы для CRUD операций над проектами.
    Каждый пользователь видит и управляет только своими проектами.
    """

    async def get_projects(self, user_id) -> list[Project]:
        """Получает список всех проектов пользователя.

        Args:
            user_id: ID владельца проектов.

        Returns:
            Список проектов пользователя.
        """
        return await self.db.projects.get_filtered(owner_id=user_id)

    async def get_project(self, project_id, user_id) -> Project:
        """Получает проект пользователя по ID.

        Args:
            project_id: ID проекта.
            user_id: ID владельца.

        Returns:
            Найденный проект.

        Raises:
            NotFoundError: Проект не найден.
        """
        try:
            return await self.db.projects.get_filtered_one(owner_id=user_id, id=project_id)
        except NotFoundError:
            raise NotFoundError(f"Проект с id {project_id} не найден")

    async def create_project(self, user_id: int, data: ProjectRequest) -> Project:
        """Создаёт новый проект.

        Args:
            user_id: ID владельца проекта.
            data: Данные для создания проекта.

        Returns:
            Созданный проект.

        Raises:
            ConflictError: Проект с таким названием уже существует у пользователя.
        """
        try:
            project = await self.db.projects.create(data={**data.model_dump(), "owner_id": user_id})
            await self.db.commit()
            return project
        except ConflictError:
            raise ConflictError(f"Проект с названием {data.title} уже существует")

    async def edit_project(self, project_id: int, user_id: int, data: ProjectPUT) -> Project:
        """Полностью обновляет проект (PUT).

        Args:
            project_id: ID проекта.
            user_id: ID владельца.
            data: Полные новые данные проекта.

        Returns:
            Обновлённый проект.

        Raises:
            NotFoundError: Проект не найден.
            ConflictError: Проект с таким названием уже существует.
        """
        try:
            await self.check_project_exists(project_id, user_id)
            project = await self.db.projects.update(
                data={**data.model_dump(), "owner_id": user_id}, id=project_id
            )
            await self.db.commit()
            return project
        except ConflictError:
            raise ConflictError(f"Проект с названием {data.title} уже существует")

    async def update_project(self, project_id: int, user_id: int, data: ProjectUpdate) -> Project:
        """Частично обновляет проект (PATCH).

        Args:
            project_id: ID проекта.
            user_id: ID владельца.
            data: Частичные данные для обновления.

        Returns:
            Обновлённый проект.

        Raises:
            NotFoundError: Проект не найден.
            ConflictError: Проект с таким названием уже существует.
        """
        try:
            await self.check_project_exists(project_id, user_id)
            project = await self.db.projects.update(
                data={**data.model_dump(exclude_unset=True), "owner_id": user_id}, id=project_id
            )
            await self.db.commit()
            return project
        except ConflictError:
            raise ConflictError(f"Проект с названием {data.title} уже существует")

    async def delete_project(self, project_id: int, user_id: int) -> None:
        """Удаляет проект.

        Все задачи проекта будут удалены каскадно.

        Args:
            project_id: ID проекта.
            user_id: ID владельца.

        Raises:
            NotFoundError: Проект не найден.
        """
        await self.check_project_exists(project_id, user_id)
        await self.db.projects.delete(project_id)
        await self.db.commit()
