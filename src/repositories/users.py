from sqlalchemy import or_, select

from src.models import UserOrm
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = UserOrm

    async def user_exists(self, email: str, username: str) -> UserOrm | None:
        query = select(self.model).where(
            or_(
                self.model.email == email,
                self.model.username == username
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()