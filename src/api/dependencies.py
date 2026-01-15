"""FastAPI зависимости для Dependency Injection.

Содержит зависимости для получения текущего пользователя,
сервисов и Unit of Work.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ForbiddenError, NotAuthorizedError, NotFoundError
from src.database import get_db
from src.models import UserOrm
from src.services.auth import AuthService
from src.services.categories import CategoryService
from src.services.projects import ProjectService
from src.services.tasks import TaskServiceDep
from src.services.users import UserService
from src.uow.uow import UnitOfWork


async def get_db_manager():
    """Создаёт Unit of Work для текущего запроса.

    Yields:
        UnitOfWork: Экземпляр с активной сессией и репозиториями.
    """
    async with UnitOfWork() as db:
        yield db


async def get_task_service(db: UnitOfWork = Depends(get_db_manager)) -> TaskServiceDep:
    """Создаёт сервис задач.

    Args:
        db: Unit of Work из зависимости.

    Returns:
        Экземпляр TaskServiceDep.
    """
    return TaskServiceDep(db)


async def get_project_service(db: UnitOfWork = Depends(get_db_manager)) -> ProjectService:
    """Создаёт сервис проектов.

    Args:
        db: Unit of Work из зависимости.

    Returns:
        Экземпляр ProjectService.
    """
    return ProjectService(db)


async def get_user_service(db: UnitOfWork = Depends(get_db_manager)) -> UserService:
    """Создаёт сервис пользователей.

    Args:
        db: Unit of Work из зависимости.

    Returns:
        Экземпляр UserService.
    """
    return UserService(db)


async def get_category_service(db: UnitOfWork = Depends(get_db_manager)) -> CategoryService:
    """Создаёт сервис категорий.

    Args:
        db: Unit of Work из зависимости.

    Returns:
        Экземпляр CategoryService.
    """
    return CategoryService(db)


async def get_auth_service(db: UnitOfWork = Depends(get_db_manager)) -> AuthService:
    """Создаёт сервис аутентификации.

    Args:
        db: Unit of Work из зависимости.

    Returns:
        Экземпляр AuthService.
    """
    return AuthService(db)


# Type aliases для Dependency Injection
DBDep = Annotated[AsyncSession, Depends(get_db)]
"""Зависимость для получения AsyncSession напрямую."""

DBManagerDep = Annotated[UnitOfWork, Depends(get_db_manager)]
"""Зависимость для получения Unit of Work."""

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
"""Зависимость для получения AuthService."""

TaskServiceDep = Annotated[TaskServiceDep, Depends(get_task_service)]
"""Зависимость для получения TaskService."""

ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
"""Зависимость для получения ProjectService."""

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
"""Зависимость для получения UserService."""

CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
"""Зависимость для получения CategoryService."""


async def get_current_user(service: AuthServiceDep, request: Request):
    """Получает текущего аутентифицированного пользователя.

    Извлекает access_token из cookies и валидирует его.

    Args:
        service: Сервис аутентификации.
        request: HTTP запрос с cookies.

    Returns:
        Текущий пользователь.

    Raises:
        HTTPException 401: Токен отсутствует или невалиден.
        HTTPException 404: Пользователь не найден.
    """
    access_token = request.cookies.get("access_token")

    try:
        return await service.get_user_by_token(access_token)
    except NotFoundError as e:
        raise HTTPException(404, e.message)
    except NotAuthorizedError as e:
        raise HTTPException(401, e.message)


CurrentUserDep = Annotated[UserOrm | None, Depends(get_current_user)]
"""Зависимость для получения текущего пользователя."""


async def get_current_user_id(user: CurrentUserDep):
    """Получает ID текущего пользователя.

    Args:
        user: Текущий пользователь из зависимости.

    Returns:
        ID пользователя.
    """
    return user.id


CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]
"""Зависимость для получения ID текущего пользователя."""


async def user_is_superuser(service: AuthServiceDep, user: UserOrm = Depends(get_current_user)):
    """Проверяет права суперпользователя.

    Args:
        service: Сервис аутентификации.
        user: Текущий пользователь.

    Returns:
        True если пользователь является суперпользователем.

    Raises:
        HTTPException 403: Недостаточно прав.
    """
    try:
        await service.verify_superuser(user)
        return True
    except ForbiddenError as e:
        raise HTTPException(403, e.message)


UserIsSuperuserDep = Annotated[bool, Depends(user_is_superuser)]
"""Зависимость для проверки прав суперпользователя."""
