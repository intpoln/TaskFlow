from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import DBDep
from src.models.categories import CategoryOrm
from src.schemas.categories import Category, CategoryAdd
from src.utils.auth import user_is_superuser

router = APIRouter(prefix='/categories', tags=['categories'])


@router.get("", response_model=list[Category])
@cache(expire=10)
async def get_categories(db: DBDep):
    query = select(CategoryOrm)
    result = await db.execute(query)
    return result.scalars().all()

@router.post('', response_model=Category, dependencies=[Depends(user_is_superuser)])
async def create_category(db: DBDep, data: CategoryAdd):
    try:
        add_stmt = insert(CategoryOrm).values(title=data.title).returning(CategoryOrm)
        res = await db.execute(add_stmt)
        category = res.scalar_one()
        await db.commit()
        return category
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, 'Такая категория уже существует')