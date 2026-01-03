from pydantic import BaseModel, EmailStr


class TaskAdd(BaseModel):
    name: str

class Task(TaskAdd):
    id: int