from src.core.exceptions import ConflictError
from src.schemas.categories import Category, CategoryAdd, CategoryUpdate
from src.services.base import BaseService


class CategoryService(BaseService):
    async def get_categories(self) -> list[Category]:
        return await self.db.categories.get_all()

    async def get_category(self, category_id: int) -> Category:
        return await self.db.categories.get_by_id(category_id)

    async def create_category(self, data: CategoryAdd) -> Category:
        try:
            category = await self.db.categories.create(data.model_dump())
            await self.db.commit()
            return category
        except ConflictError:
            raise ConflictError(f"Категория с названием {data.title} уже существует")

    async def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        try:
            category = await self.db.categories.update(id=category_id, data=data.model_dump())
            await self.db.commit()
            return category
        except ConflictError:
            raise ConflictError(f"Категория с названием {data.title} уже существует")

    async def delete_category(self, category_id: int) -> None:
        category = await self.db.categories.delete(category_id)
        await self.db.commit()
        return category
