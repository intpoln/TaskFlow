from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import UserOrm
from src.services.auth import AuthService


async def get_current_user_id(request: Request) -> int:
    access_token = request.cookies.get('access_token')

    if not access_token:
        raise HTTPException(401, "Сначала авторизуйтесь")

    user_id = AuthService.get_user_id_from_token(access_token)
    if not user_id:
        raise HTTPException(401, "Сначала авторизуйтесь")

    return user_id


async def get_current_user(db: AsyncSession = Depends(get_db),
                           user_id: int = Depends(get_current_user_id)) -> UserOrm:
    query = select(UserOrm).filter_by(id=user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, 'Несуществующий пользователь')

    return user


async def user_is_superuser(user: UserOrm = Depends(get_current_user)) -> bool:
    if not user.is_superuser:
        raise HTTPException(403, 'Недостаточно прав')

    return True
