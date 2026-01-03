from datetime import datetime

from pydantic import BaseModel


class TaskAdd(BaseModel):
   category: int | None = None
   description: str
   date_from: datetime | None = None
   date_to: datetime | None = None

class TaskUpdate(BaseModel):
    category: int | None = None
    description: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

class Task(BaseModel):
    id: int
    category: int
    description: str
    date_from: datetime
    date_to: datetime