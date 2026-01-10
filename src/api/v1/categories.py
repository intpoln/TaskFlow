from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import DBDep
from src.models.categories import CategoryOrm
from src.schemas.categories import Category, CategoryAdd
from src.utils.auth import get_current_user, user_is_superuser

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[Category], dependencies=[Depends(get_current_user)])
@cache(expire=15)
async def get_categories(db: DBDep):
    query = select(CategoryOrm)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=Category, dependencies=[Depends(user_is_superuser)])
async def create_category(db: DBDep, data: CategoryAdd):
    try:
        add_stmt = insert(CategoryOrm).values(title=data.title).returning(CategoryOrm)
        res = await db.execute(add_stmt)
        category = res.scalar_one()
        await db.commit()
        return category
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Такая категория уже существует")


@router.get("/{category_id}", dependencies=[Depends(get_current_user)])
async def get_category(db: DBDep, category_id: int):
    query = select(CategoryOrm).filter_by(id=category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(404, "Категория не найдена")
    return category


@router.patch("/{category_id}", dependencies=[Depends(user_is_superuser)])
async def update_category(db: DBDep, category_id: int, data: CategoryAdd):
    query = select(CategoryOrm).filter_by(id=category_id)
    res = await db.execute(query)
    category = res.scalar_one_or_none()
    if not category:
        raise HTTPException(404, "Категория не найдена")
    try:  # Сначала убедиться в существовании категории!
        edit_stmt = update(CategoryOrm).filter_by(id=category_id).values(title=data.title)
        await db.execute(edit_stmt)
        await db.commit()
        return {"status": True}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Такая категория уже существует")


@router.delete("/{category_id}", dependencies=[Depends(user_is_superuser)])
async def delete_category(db: DBDep, category_id: int):
    try:  # Сначала убедиться в существовании категории!
        delete_stmt = delete(CategoryOrm).filter_by(id=category_id)
        await db.execute(delete_stmt)
        await db.commit()
        return {"status": True}
    except IntegrityError:  #  Здесь не будет такого исключения
        await db.rollback()
        return {"status": False}
