from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from sqlalchemy import select

from src.api.dependencies import DBDep, user_is_superuser
from src.models.users import UserOrm
from src.schemas.users import User

router = APIRouter(prefix='/users', tags=['Users'])


@router.get("", response_model=list[User], dependencies=[Depends(user_is_superuser)])
@cache(expire=15)
async def get_users(db: DBDep):
    query = select(UserOrm)
    result = await db.execute(query)
    return result.scalars().all()
