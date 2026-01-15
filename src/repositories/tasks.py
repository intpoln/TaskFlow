"""Репозиторий для работы с задачами.

Содержит методы для получения и поиска задач пользователя.
"""

from sqlalchemy import or_, select

from src.core.exceptions import NotFoundError
from src.models import CategoryOrm, ProjectOrm, TaskOrm
from src.repositories.base import BaseRepository


class TaskRepository(BaseRepository[TaskOrm]):
    """Репозиторий задач пользователя.

    Расширяет BaseRepository методами для работы
    с задачами: поиск, фильтрация по статусу и т.д.
    """

    model = TaskOrm

    async def get_user_tasks(
        self, user_id: int, search: str | None = None, status: str | None = None
    ) -> list[TaskOrm]:
        """Получает список задач пользователя с фильтрацией.

        Поддерживает поиск по названию/описанию задачи,
        названию проекта и категории. Поиск регистронезависимый.

        Args:
            user_id: ID владельца задач.
            search: Поисковый запрос (опционально).
            status: Фильтр по статусу (TODO, IN_PROGRESS, DONE).

        Returns:
            Список задач, соответствующих критериям.
        """
        query = select(self.model).filter_by(owner_id=user_id)

        if search:
            pattern = f"%{search}%"
            query = query.outerjoin(ProjectOrm).outerjoin(CategoryOrm)
            query = query.where(
                or_(
                    self.model.title.ilike(pattern),
                    self.model.description.ilike(pattern),
                    ProjectOrm.title.ilike(pattern),
                    CategoryOrm.title.ilike(pattern),
                )
            )

        if status:
            query = query.where(self.model.status == status)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_task(self, task_id: int, user_id: int) -> TaskOrm:
        """Получает задачу пользователя по ID.

        Проверяет что задача принадлежит указанному пользователю.

        Args:
            task_id: ID задачи.
            user_id: ID владельца.

        Returns:
            Найденная задача.

        Raises:
            NotFoundError: Задача не найдена или принадлежит другому пользователю.
        """
        query = select(self.model).filter_by(id=task_id, owner_id=user_id)
        result = await self.session.execute(query)
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError(f"Задача с id {task_id} не найдена")
        return task
