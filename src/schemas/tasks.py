from datetime import datetime, timedelta

from pydantic import BaseModel

from src.models.tasks import TaskStatus


class TaskRequest(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    deadline: datetime = datetime.now() + timedelta(days=1)
    notify: bool = False
    project_id: int

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
