from sqlalchemy import or_, select

from src.models import UserOrm
from src.repositories.base import BaseRepository
from src.schemas.users import User


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

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(self.model).filter_by(id=user_id)
        result = await self.session.execute(query)
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            return None
        return User.model_validate(orm_user)