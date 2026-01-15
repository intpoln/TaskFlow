"""API эндпоинты для пользователей.

Содержит административные эндпоинты для работы с пользователями.
"""

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from src.api.dependencies import UserServiceDep, user_is_superuser
from src.schemas.users import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=list[User],
    dependencies=[Depends(user_is_superuser)],
    summary="Получение списка всех пользователей (только для суперюзера)",
)
@cache(expire=15)
async def get_users(service: UserServiceDep):
    """Получает список всех пользователей.

    Доступно только суперпользователям.
    Результат кэшируется на 15 секунд.

    Args:
        service: Сервис пользователей.

    Returns:
        Список всех зарегистрированных пользователей.
    """
    return await service.get_users()
