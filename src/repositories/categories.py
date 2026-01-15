"""Репозиторий для работы с категориями.

Наследует базовые CRUD операции от BaseRepository.
"""

from src.models import CategoryOrm
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[CategoryOrm]):
    """Репозиторий категорий задач.

    Использует стандартные CRUD операции из BaseRepository.
    При необходимости можно добавить специфичные методы.
    """

    model = CategoryOrm
