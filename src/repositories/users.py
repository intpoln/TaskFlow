from src.models import UserOrm
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = UserOrm