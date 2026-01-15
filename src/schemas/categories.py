"""Pydantic схемы для категорий задач.

Содержит схемы для создания, обновления и отображения категорий.
"""

from pydantic import BaseModel


class CategoryAdd(BaseModel):
    """Схема создания новой категории.

    Attributes:
        title: Название категории.
    """

    title: str


class Category(CategoryAdd):
    """Схема категории для API ответов.

    Attributes:
        id: Уникальный идентификатор.
        title: Название категории.
    """

    id: int


class CategoryUpdate(BaseModel):
    """Схема обновления категории (PATCH).

    Attributes:
        title: Новое название категории.
    """

    title: str
