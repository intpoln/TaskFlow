from datetime import datetime, timedelta

from pydantic import BaseModel, Field, field_validator

from src.models.tasks import TaskStatus


def default_deadline():
    return datetime.now() + timedelta(days=1)


class TaskRequest(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    deadline: datetime = Field(default_factory=default_deadline)
    notify: bool = False
    project_id: int
    category_id: int | None = None

    @field_validator("category_id", mode="before")
    @classmethod
    def convert_zero_to_none(cls, value):
        if value == 0 or value == "":
            return None
        return value


class TaskAdd(TaskRequest):
    owner_id: int


class Task(TaskAdd):
    id: int
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
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
        if value == 0 or value == "":
            return None
        return value


class TaskPUT(BaseModel):
    title: str
    description: str
    status: TaskStatus
    deadline: datetime
    notify: bool
    project_id: int
    category_id: int

    @field_validator("category_id", mode="before")
    @classmethod
    def convert_zero_to_none(cls, value):
        if value == 0 or value == "":
            return None
        return value
