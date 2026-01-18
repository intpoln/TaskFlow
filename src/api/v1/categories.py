"""API эндпоинты для категорий задач.

Содержит CRUD эндпоинты для управления категориями.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache

from src.api.dependencies import CategoryServiceDep, get_current_user, user_is_superuser
from src.core.exceptions import ConflictError, NotFoundError
from src.schemas.categories import Category, CategoryAdd, CategoryUpdate

router = APIRouter(prefix="/v1/categories", tags=["Категории"])


@router.get(
    "",
    response_model=list[Category],
    dependencies=[Depends(get_current_user)],
    summary="Получение всех категорий",
)
@cache(expire=60)
async def get_categories(service: CategoryServiceDep):
    """Получает список всех категорий.

    Доступно авторизованным пользователям.
    Результат кэшируется на 15 секунд.

    Args:
        service: Сервис категорий.

    Returns:
        Список всех категорий.
    """
    return await service.get_categories()


@router.post(
    "",
    response_model=Category,
    dependencies=[Depends(user_is_superuser)],
    summary="Создание категории (только для суперюзера)",
    status_code=201,
)
async def create_category(service: CategoryServiceDep, data: CategoryAdd):
    """Создает новую категорию.

    Доступно только суперпользователям.

    Args:
        service: Сервис категорий.
        data: Данные для создания категории.

    Returns:
        Созданная категория.

    Raises:
        HTTPException 409: Категория с таким названием уже существует.
    """
    try:
        return await service.create_category(data)
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.get(
    "/{category_id}",
    dependencies=[Depends(get_current_user)],
    summary="Получение отдельной категории",
)
@cache(expire=60)
async def get_category(service: CategoryServiceDep, category_id: int):
    """Получает категорию по ID.

    Args:
        service: Сервис категорий.
        category_id: ID категории.

    Returns:
        Найденная категория.

    Raises:
        HTTPException 404: Категория не найдена.
    """
    try:
        return await service.get_category(category_id)
    except NotFoundError:
        raise HTTPException(404, f"Категория с id {category_id} не найдена")


@router.patch(
    "/{category_id}",
    dependencies=[Depends(user_is_superuser)],
    summary="Обновление отдельной категории",
)
async def update_category(service: CategoryServiceDep, category_id: int, data: CategoryUpdate):
    """Обновляет категорию.

    Доступно только суперпользователям.

    Args:
        service: Сервис категорий.
        category_id: ID категории.
        data: Новые данные категории.

    Returns:
        Обновленная категория.

    Raises:
        HTTPException 404: Категория не найдена.
        HTTPException 409: Категория с таким названием уже существует.
    """
    try:
        return await service.update_category(category_id, data)
    except NotFoundError:
        raise HTTPException(404, f"Категория с id {category_id} не найдена")
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.delete(
    "/{category_id}", dependencies=[Depends(user_is_superuser)], summary="Удаление категории"
)
async def delete_category(service: CategoryServiceDep, category_id: int):
    """Удаляет категорию.

    Доступно только суперпользователям.

    Args:
        service: Сервис категорий.
        category_id: ID категории.

    Returns:
        Результат удаления.

    Raises:
        HTTPException 404: Категория не найдена.
    """
    try:
        await service.delete_category(category_id)
        return {"status": True}
    except NotFoundError:
        raise HTTPException(404, f"Категория с id {category_id} не найдена")
