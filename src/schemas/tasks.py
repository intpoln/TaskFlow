from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from src.models.tasks import TaskStatus

def default_deadline():
    return datetime.now() + timedelta(days=1)


class TaskRequest(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    deadline: datetime = Field(default_factory=default_deadline)
    notify: bool = False
    project_id: int | None = None
    category_id: int | None = None

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
