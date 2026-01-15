"""Сервис для работы с задачами.

Содержит бизнес-логику управления задачами пользователей.
"""

from src.core.exceptions import ConflictError
from src.schemas.tasks import Task, TaskPUT, TaskRequest, TaskUpdate
from src.services.base import BaseService


class TaskServiceDep(BaseService):
    """Сервис управления задачами.

    Предоставляет методы для CRUD операций над задачами.
    Включает валидацию связей с проектами и категориями.
    """

    async def get_tasks(
        self, user_id: int, search: str | None = None, status: str | None = None
    ) -> list[Task]:
        """Получает список задач пользователя с фильтрацией.

        Args:
            user_id: ID владельца задач.
            search: Поисковый запрос (название, описание, проект, категория).
            status: Фильтр по статусу (TODO, IN_PROGRESS, DONE).

        Returns:
            Список задач, соответствующих критериям.
        """
        return await self.db.tasks.get_user_tasks(user_id=user_id, search=search, status=status)

    async def get_task(self, task_id: int, user_id) -> Task:
        """Получает задачу пользователя по ID.

        Args:
            task_id: ID задачи.
            user_id: ID владельца.

        Returns:
            Найденная задача.

        Raises:
            NotFoundError: Задача не найдена.
        """
        return await self.db.tasks.get_user_task(task_id=task_id, user_id=user_id)

    async def create_task(self, user_id: int, data: TaskRequest) -> Task:
        """Создаёт новую задачу.

        Проверяет существование проекта и категории перед созданием.

        Args:
            user_id: ID владельца задачи.
            data: Данные для создания задачи.

        Returns:
            Созданная задача.

        Raises:
            NotFoundError: Проект или категория не найдены.
            ConflictError: Задача с таким названием уже существует в проекте.
        """
        await self.check_project_category_exists(data.project_id, user_id, data.category_id)

        try:
            task = await self.db.tasks.create(
                {
                    **data.model_dump(exclude_unset=True),
                    "owner_id": user_id,
                }
            )
            await self.db.commit()
            return task
        except ConflictError:
            raise ConflictError(f"Задача с названием {data.title} уже существует")

    async def edit_task(self, task_id: int, user_id: int, data: TaskPUT) -> Task:
        """Полностью обновляет задачу (PUT).

        Args:
            task_id: ID задачи.
            user_id: ID владельца.
            data: Полные новые данные задачи.

        Returns:
            Обновлённая задача.

        Raises:
            NotFoundError: Задача, проект или категория не найдены.
            ConflictError: Задача с таким названием уже существует в проекте.
        """
        await self.check_project_category_exists(data.project_id, user_id, data.category_id)
        await self.check_task_exists(task_id, user_id)

        try:
            task = await self.db.tasks.update(
                data={**data.model_dump(), "owner_id": user_id}, id=task_id
            )
            await self.db.commit()
            return task
        except ConflictError:
            raise ConflictError(f"Задача с названием {data.title} уже существует")

    async def update_task(self, task_id: int, user_id: int, data: TaskUpdate) -> Task:
        """Частично обновляет задачу (PATCH).

        Args:
            task_id: ID задачи.
            user_id: ID владельца.
            data: Частичные данные для обновления.

        Returns:
            Обновлённая задача.

        Raises:
            NotFoundError: Задача не найдена.
            ConflictError: Задача с таким названием уже существует в проекте.
        """
        existed_task = await self.check_task_exists(task_id, user_id)

        await self.check_project_category_exists(
            existed_task.project_id, user_id, existed_task.category_id
        )

        try:
            task = await self.db.tasks.update(
                data={**data.model_dump(exclude_unset=True), "owner_id": user_id}, id=task_id
            )
            await self.db.commit()
            return task
        except ConflictError:
            raise ConflictError(f"Задача с названием {data.title} уже существует")

    async def delete_task(self, task_id: int, user_id: int) -> None:
        """Удаляет задачу.

        Args:
            task_id: ID задачи.
            user_id: ID владельца.

        Raises:
            NotFoundError: Задача не найдена.
        """
        await self.check_task_exists(task_id, user_id)
        await self.db.tasks.delete(id=task_id)
        await self.db.commit()
