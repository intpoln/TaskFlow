import logging
from typing import Generic, Type, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError, NotFoundError, RepositoryError
from src.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType] = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        query = select(self.model).filter_by(id=id)
        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundError(f"{self.model.__name__} с id {id} не найден")
        return obj

    async def get_filtered(self, **filters) -> list[ModelType]:
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_filtered_one(self, **filters) -> ModelType | None:
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundError(f"{self.model.__name__} не найден")
        return obj

    async def get_all(self) -> list[ModelType]:
        return await self.get_filtered()

    async def create(self, data: dict) -> ModelType | None:
        try:
            add_stmt = insert(self.model).values(**data).returning(self.model)
            result = await self.session.execute(add_stmt)
            return result.scalar_one()
        except IntegrityError as e:
            await self.session.rollback()
            self._handle_integrity_error(e)

    async def update(self, id: int, data: dict, **filters) -> ModelType | None:
        try:
            update_stmt = (
                update(self.model)
                .where(self.model.id == id)
                .filter_by(**filters)
                .values(**data)
                .returning(self.model)
            )
            result = await self.session.execute(update_stmt)
            updated = result.scalar_one_or_none()
            if not updated:
                raise NotFoundError(f"{self.model.__name__} с id {id} не найден")
            return updated
        except IntegrityError as e:
            await self.session.rollback()
            self._handle_integrity_error(e)

    async def delete(self, id: int) -> bool:
        delete_stmt = delete(self.model).filter_by(id=id).returning(self.model)
        result = await self.session.execute(delete_stmt)
        deleted = result.scalar_one_or_none()
        if not deleted:
            raise NotFoundError(f"{self.model.__name__} с id {id} не найден")
        return True

    def _handle_integrity_error(self, error: IntegrityError):
        error_code = getattr(error.orig, "pgcode", None)
        error_message = str(error.orig)

        if error_code == "23505":  # UniqueViolation
            raise ConflictError("Запись с такими данными уже существует")

        if error_code == "23503":  # Foreign Key Violation
            raise RepositoryError("Связанная запись не найдена")

        if error_code == "23514":  # Check Violation
            raise RepositoryError("Нарушение ограничения данных")

        if error_code == "23502":  # Not Null Violation
            raise RepositoryError("Обязательное поле не заполнено")

        logging.error(f"Неизвестная IntegrityError: {error_code} - {error_message}")
        raise RepositoryError("Ошибка целостности данных")
