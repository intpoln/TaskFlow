from pydantic import BaseModel


class TaskAdd(BaseModel):
    name: str


class Task(TaskAdd):
    id: int
