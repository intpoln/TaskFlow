from src.schemas.categories import CategoryAdd
from src.uow.uow import UnitOfWork

async def test_create_category():
    data = CategoryAdd(title='test category')
    async with UnitOfWork() as db:
        category = await db.categories.create(data.model_dump())
        print(f"{category=}")
        await db.commit()