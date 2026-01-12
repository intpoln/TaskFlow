from typing import Generic, Type, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType] = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        query = select(self.model).filter_by(id=id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_filtered(self, **filters) -> list[ModelType]:
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self) -> list[ModelType]:
        return await self.get_filtered()

    async def create(self, data: dict) -> ModelType:
        add_stmt = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(add_stmt)
        return result.scalar_one()

    async def update(self, id: int, data: dict, **filters) -> ModelType | None:
        update_stmt = (
            update(self.model)
            .where(self.model.id == id)
            .filter_by(**filters)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(update_stmt)
        return result.scalar_one_or_none()

    async def delete(self, id: int) -> None:
        delete_stmt = delete(self.model).filter_by(id=id)
        await self.session.execute(delete_stmt)
