from src.models import CategoryOrm
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    model = CategoryOrm
