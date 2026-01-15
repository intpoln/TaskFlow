"""Сервис для работы с категориями задач.

Содержит бизнес-логику управления категориями.
"""

from src.core.exceptions import ConflictError
from src.schemas.categories import Category, CategoryAdd, CategoryUpdate
from src.services.base import BaseService


class CategoryService(BaseService):
    """Сервис управления категориями.

    Предоставляет методы для CRUD операций над категориями.
    Создание, обновление и удаление доступны только суперпользователям.
    """

    async def get_categories(self) -> list[Category]:
        """Получает список всех категорий.

        Returns:
            Список всех категорий.
        """
        return await self.db.categories.get_all()

    async def get_category(self, category_id: int) -> Category:
        """Получает категорию по ID.

        Args:
            category_id: ID категории.

        Returns:
            Найденная категория.

        Raises:
            NotFoundError: Категория не найдена.
        """
        return await self.db.categories.get_by_id(category_id)

    async def create_category(self, data: CategoryAdd) -> Category:
        """Создаёт новую категорию.

        Args:
            data: Данные для создания категории.

        Returns:
            Созданная категория.

        Raises:
            ConflictError: Категория с таким названием уже существует.
        """
        try:
            category = await self.db.categories.create(data.model_dump())
            await self.db.commit()
            return category
        except ConflictError:
            raise ConflictError(f"Категория с названием {data.title} уже существует")

    async def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        """Обновляет существующую категорию.

        Args:
            category_id: ID категории для обновления.
            data: Новые данные категории.

        Returns:
            Обновлённая категория.

        Raises:
            NotFoundError: Категория не найдена.
            ConflictError: Категория с таким названием уже существует.
        """
        try:
            category = await self.db.categories.update(id=category_id, data=data.model_dump())
            await self.db.commit()
            return category
        except ConflictError:
            raise ConflictError(f"Категория с названием {data.title} уже существует")

    async def delete_category(self, category_id: int) -> None:
        """Удаляет категорию.

        Args:
            category_id: ID категории для удаления.

        Raises:
            NotFoundError: Категория не найдена.
        """
        category = await self.db.categories.delete(category_id)
        await self.db.commit()
        return category
