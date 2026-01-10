from src.services.base import BaseService


class UserService(BaseService):

    async def get_users(self):
        return self.db.users.get_all()