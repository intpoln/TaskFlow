from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import UserOrm
from src.utils.auth import get_current_user_id, get_current_user, user_is_superuser

DBDep = Annotated[AsyncSession, Depends(get_db)]


CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]
CurrentUserDep = Annotated[UserOrm, Depends(get_current_user)]
UserIsSuperuserDep = Annotated[bool, Depends(user_is_superuser)]