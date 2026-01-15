"""Unit of Work паттерн для управления транзакциями.

Обеспечивает единую точку управления сессией БД
и доступ ко всем репозиториям.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.repositories.categories import CategoryRepository
from src.repositories.projects import ProjectRepository
from src.repositories.tasks import TaskRepository
from src.repositories.users import UserRepository


class UnitOfWork:
    """Unit of Work - управление транзакциями БД.

    Реализует паттерн UoW для координации работы нескольких репозиториев
    в рамках одной транзакции. Используется как асинхронный контекстный менеджер.

    Attributes:
        session: Асинхронная сессия SQLAlchemy.
        tasks: Репозиторий задач.
        projects: Репозиторий проектов.
        categories: Репозиторий категорий.
        users: Репозиторий пользователей.

    Example:
        >>> async with UnitOfWork() as uow:
        ...     user = await uow.users.get_by_id(1)
        ...     await uow.tasks.create({"title": "Task", "owner_id": user.id})
        ...     await uow.commit()
    """

    def __init__(self):
        """Инициализирует UoW с фабрикой сессий."""
        self.session_factory = async_session_maker

    async def __aenter__(self):
        """Создаёт сессию и инициализирует репозитории.

        Returns:
            self: Экземпляр UnitOfWork с активной сессией.
        """
        self.session: AsyncSession = self.session_factory()

        self.tasks = TaskRepository(self.session)
        self.projects = ProjectRepository(self.session)
        self.categories = CategoryRepository(self.session)
        self.users = UserRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Откатывает транзакцию и закрывает сессию.

        При выходе из контекста всегда выполняется rollback
        для отмены незакоммиченных изменений.

        Args:
            exc_type: Тип исключения (если было).
            exc_val: Значение исключения.
            exc_tb: Traceback исключения.
        """
        await self.rollback()
        await self.session.close()

    async def commit(self):
        """Фиксирует текущую транзакцию.

        Сохраняет все изменения в БД. Вызывайте после
        успешного выполнения всех операций.
        """
        await self.session.commit()

    async def rollback(self):
        """Откатывает текущую транзакцию.

        Отменяет все незафиксированные изменения.
        Автоматически вызывается при выходе из контекста.
        """
        await self.session.rollback()
