"""ORM модель категории задач.

Содержит модель CategoryOrm для классификации задач.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class CategoryOrm(Base):
    """Модель категории в базе данных.

    Категории используются для группировки задач
    по типу или области (работа, личное, учёба и т.д.).

    Attributes:
        id: Уникальный идентификатор категории.
        title: Название категории (уникальное, до 30 символов).
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30), unique=True)
