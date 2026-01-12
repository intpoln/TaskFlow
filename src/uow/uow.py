from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.repositories.categories import CategoryRepository
from src.repositories.projects import ProjectRepository
from src.repositories.tasks import TaskRepository
from src.repositories.users import UserRepository


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()

        self.tasks = TaskRepository(self.session)
        self.projects = ProjectRepository(self.session)
        self.categories = CategoryRepository(self.session)
        self.users = UserRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
