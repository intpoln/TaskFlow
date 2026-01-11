from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from src.api.dependencies import user_is_superuser, UserServiceDep
from src.schemas.users import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[User], dependencies=[Depends(user_is_superuser)])
@cache(expire=15)
async def get_users(service: UserServiceDep):
    return await service.get_users()