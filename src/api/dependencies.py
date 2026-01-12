from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import UserOrm
from src.services.auth import AuthService
from src.services.categories import CategoryService
from src.services.projects import ProjectService
from src.services.tasks import TaskService
from src.services.users import UserService
from src.uow.uow import UnitOfWork
from src.utils.auth import get_current_user, get_current_user_id, user_is_superuser


async def get_db_manager():
    async with UnitOfWork() as db:
        yield db


async def get_task_service(db: UnitOfWork = Depends(get_db_manager)) -> TaskService:
    return TaskService(db)


async def get_project_service(db: UnitOfWork = Depends(get_db_manager)) -> ProjectService:
    return ProjectService(db)


async def get_user_service(db: UnitOfWork = Depends(get_db_manager)) -> UserService:
    return UserService(db)


async def get_category_service(db: UnitOfWork = Depends(get_db_manager)) -> CategoryService:
    return CategoryService(db)


async def get_auth_service(db: UnitOfWork = Depends(get_db_manager)) -> AuthService:
    return AuthService(db)


DBDep = Annotated[AsyncSession, Depends(get_db)]
DBManagerDep = Annotated[UnitOfWork, Depends(get_db_manager)]

CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]
CurrentUserDep = Annotated[UserOrm, Depends(get_current_user)]
UserIsSuperuserDep = Annotated[bool, Depends(user_is_superuser)]

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
