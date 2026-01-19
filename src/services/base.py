"""Базовый сервис с общими методами проверки.

Содержит базовый класс для всех сервисов приложения.
"""

from src.core.exceptions import NotFoundError
from src.schemas.tasks import Task
from src.uow.uow import UnitOfWork


class BaseService:
    """Базовый класс сервиса.

    Предоставляет доступ к Unit of Work и общие методы
    проверки существования сущностей.

    Attributes:
        db: Unit of Work для работы с репозиториями.

    Example:
        >>> class TaskService(BaseService):
        ...     async def get_tasks(self, user_id: int):
        ...         return await self.db.tasks.get_user_tasks(user_id)
    """

    db: UnitOfWork

    def __init__(self, db: UnitOfWork):
        """Инициализирует сервис с Unit of Work.

        Args:
            db: Unit of Work с репозиториями.
        """
        self.db = db

    async def check_project_exists(self, project_id: int, user_id: int) -> bool:
        """Проверяет существование проекта у пользователя.

        Args:
            project_id: ID проекта.
            user_id: ID владельца.

        Returns:
            True если проект существует.

        Raises:
            NotFoundError: Проект не найден.
        """
        project = await self.db.projects.get_user_project(project_id, user_id)

        if not project:
            raise NotFoundError("Проект не найден")

        return True

    async def check_category_exists(self, category_id: int) -> bool:
        """Проверяет существование категории.

        Args:
            category_id: ID категории.

        Returns:
            True если категория существует.

        Raises:
            NotFoundError: Категория не найдена.
        """
        category = await self.db.categories.get_by_id(category_id)

        if not category:
            raise NotFoundError("Категория не найдена")

        return category

    async def check_task_exists(self, task_id: int, user_id: int) -> Task:
        """Проверяет существование задачи у пользователя.

        Args:
            task_id: ID задачи.
            user_id: ID владельца.

        Returns:
            Найденная задача.

        Raises:
            NotFoundError: Задача не найдена.
        """
        task = await self.db.tasks.get_user_task(task_id=task_id, user_id=user_id)

        if not task:
            raise NotFoundError("Задача не найдена")

        return task

    async def check_project_category_exists(
        self, project_id: int, user_id: int, category_id: int | None = None
    ) -> bool:
        """Проверяет существование проекта и категории.

        Используется при создании/обновлении задачи для валидации
        связанных сущностей.

        Args:
            project_id: ID проекта.
            user_id: ID владельца проекта.
            category_id: ID категории.

        Returns:
            True если обе сущности существуют.

        Raises:
            NotFoundError: Проект или категория не найдены.
        """
        await self.check_project_exists(project_id, user_id)
        if category_id:
            await self.check_category_exists(category_id)
        return True
