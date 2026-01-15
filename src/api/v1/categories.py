from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache

from src.api.dependencies import CategoryServiceDep, get_current_user, user_is_superuser
from src.core.exceptions import ConflictError, NotFoundError
from src.schemas.categories import Category, CategoryAdd, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[Category], dependencies=[Depends(get_current_user)])
@cache(expire=15)
async def get_categories(service: CategoryServiceDep):
    return await service.get_categories()


@router.post("", response_model=Category, dependencies=[Depends(user_is_superuser)])
async def create_category(service: CategoryServiceDep, data: CategoryAdd):
    try:
        return await service.create_category(data)
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.get("/{category_id}", dependencies=[Depends(get_current_user)])
async def get_category(service: CategoryServiceDep, category_id: int):
    try:
        return await service.get_category(category_id)
    except NotFoundError:
        raise HTTPException(404, f"Категория с id {category_id} не найдена")


@router.patch("/{category_id}", dependencies=[Depends(user_is_superuser)])
async def update_category(service: CategoryServiceDep, category_id: int, data: CategoryUpdate):
    try:
        return await service.update_category(category_id, data)
    except NotFoundError:
        raise HTTPException(404, f"Категория с id {category_id} не найдена")
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.delete("/{category_id}", dependencies=[Depends(user_is_superuser)])
async def delete_category(service: CategoryServiceDep, category_id: int):
    try:
        await service.delete_category(category_id)
        return {"status": True}
    except NotFoundError:
        raise HTTPException(404, f"Категория с id {category_id} не найдена")
