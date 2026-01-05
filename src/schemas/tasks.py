from datetime import datetime, timedelta

from pydantic import BaseModel

from src.models.tasks import TaskStatus


class TaskRequest(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    deadline: datetime = datetime.now() + timedelta(days=1)
    notify: bool = False

class TaskAdd(TaskRequest):
    project_id: int
    user_id: int

class Task(TaskAdd):
    id: int
    created_at: datetime
    updated_at: datetime