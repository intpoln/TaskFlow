from src.schemas.categories import Category, CategoryAdd, CategoryUpdate
from src.services.base import BaseService


class CategoryService(BaseService):

    async def get_categories(self) -> list[Category]:
        return await self.db.categories.get_all()

    async def get_category(self, category_id: int) -> Category:
        return await self.db.categories.get_by_id(category_id)

    async def create_category(self, data: CategoryAdd) -> Category:
        category = await self.db.categories.create(data)
        await self.db.commit()
        return category

    async def update_category(self, data: CategoryUpdate) -> Category:
        category = await self.db.categories.update(data)
        await self.db.commit()
        return category

    async def delete_category(self, category_id: int) -> None:
        category = await self.db.categories.delete(category_id)
        await self.db.commit()
        return category
