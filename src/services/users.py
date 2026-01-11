from src.services.base import BaseService


class UserService(BaseService):

    async def get_users(self):
        return await self.db.users.get_all()