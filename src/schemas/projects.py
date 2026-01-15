"""Pydantic схемы для проектов.

Содержит схемы для создания, обновления и отображения проектов.
"""

from datetime import datetime

from pydantic import BaseModel


class ProjectRequest(BaseModel):
    """Схема создания нового проекта (от клиента).

    Attributes:
        title: Название проекта.
        description: Описание проекта (опционально).
    """

    title: str
    description: str | None = None


class ProjectAdd(ProjectRequest):
    """Внутренняя схема для создания проекта в БД.

    Расширяет ProjectRequest, добавляя owner_id.

    Attributes:
        title: Название проекта.
        description: Описание проекта.
        owner_id: ID владельца проекта.
    """

    owner_id: int


class Project(BaseModel):
    """Схема проекта для API ответов.

    Attributes:
        id: Уникальный идентификатор.
        title: Название проекта.
        description: Описание проекта.
        owner_id: ID владельца.
        created_at: Дата создания.
    """

    id: int
    title: str
    description: str | None = None
    owner_id: int
    created_at: datetime


class ProjectUpdate(BaseModel):
    """Схема частичного обновления проекта (PATCH).

    Все поля опциональны.

    Attributes:
        title: Новое название.
        description: Новое описание.
    """

    title: str | None = None
    description: str | None = None


class ProjectPUT(BaseModel):
    """Схема полного обновления проекта (PUT).

    Все обязательные поля должны быть заполнены.

    Attributes:
        title: Название проекта.
        description: Описание проекта.
    """

    title: str
    description: str | None = None
