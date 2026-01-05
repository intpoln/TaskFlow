from fastapi import APIRouter
from fastapi_cache.decorator import cache
from sqlalchemy import select

from src.api.dependencies import DBDep
from src.models.users import UserOrm

router = APIRouter(prefix='/users')


@router.get("/")
@cache(expire=10)
async def get_users(db: DBDep):
    query = select(UserOrm)
    result = await db.execute(query)
    return result.scalars().all()
