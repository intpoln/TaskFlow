"""Pydantic схемы для задач.

Содержит схемы для создания, обновления и отображения задач,
а также вспомогательные функции и валидаторы.
"""

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field, field_validator

from src.models.tasks import TaskStatus


def default_deadline():
    """Генерирует дедлайн по умолчанию (текущее время + 1 день).

    Returns:
        datetime: Дата и время через 24 часа от текущего момента (UTC).
    """
    return datetime.now(timezone.utc) + timedelta(days=1)


class TaskRequest(BaseModel):
    """Схема создания новой задачи (от клиента).

    Attributes:
        title: Название задачи.
        description: Описание задачи.
        status: Статус выполнения (по умолчанию TODO).
        deadline: Крайний срок (по умолчанию +1 день).
        notify: Отправлять уведомление о дедлайне.
        project_id: ID проекта (обязательно).
        category_id: ID категории (опционально).
    """

    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    deadline: datetime | None = Field(
        default_factory=default_deadline, examples=[default_deadline()]
    )
    notify: bool = False
    project_id: int
    category_id: int | None = None

    @field_validator("category_id", mode="before")
    @classmethod
    def convert_zero_to_none(cls, value):
        """Конвертирует 0 или пустую строку в None.

        Swagger UI часто отправляет 0 вместо null для опциональных int полей.
        """
        if value == 0 or value == "":
            return None
        return value


class TaskAdd(TaskRequest):
    """Внутренняя схема для создания задачи в БД.

    Расширяет TaskRequest, добавляя owner_id.

    Attributes:
        owner_id: ID владельца задачи.
    """

    owner_id: int


class Task(TaskAdd):
    """Схема задачи для API ответов.

    Полная информация о задаче включая метаданные.

    Attributes:
        id: Уникальный идентификатор.
        created_at: Дата создания.
        updated_at: Дата последнего обновления.
    """

    id: int
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    """Схема частичного обновления задачи (PATCH).

    Все поля опциональны - обновляются только переданные.

    Attributes:
        title: Новое название.
        description: Новое описание.
        status: Новый статус.
        deadline: Новый дедлайн.
        notify: Новое значение флага уведомлений.
        project_id: Новый проект.
        category_id: Новая категория.
    """

    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    deadline: datetime | None = None
    notify: bool | None = None
    project_id: int | None = None
    category_id: int | None = None

    @field_validator("category_id", mode="before")
    @classmethod
    def convert_zero_to_none(cls, value):
        """Конвертирует 0 или пустую строку в None."""
        if value == 0 or value == "":
            return None
        return value


class TaskPUT(BaseModel):
    """Схема полного обновления задачи (PUT).

    Все поля обязательны для заполнения.

    Attributes:
        title: Название задачи.
        description: Описание задачи.
        status: Статус выполнения.
        deadline: Крайний срок.
        notify: Флаг уведомления.
        project_id: ID проекта.
        category_id: ID категории.
    """

    title: str
    description: str
    status: TaskStatus
    deadline: datetime | None = None
    notify: bool = False
    project_id: int
    category_id: int | None = None

    @field_validator("category_id", mode="before")
    @classmethod
    def convert_zero_to_none(cls, value):
        """Конвертирует 0 или пустую строку в None."""
        if value == 0 or value == "":
            return None
        return value
