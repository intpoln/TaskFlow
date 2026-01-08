from datetime import datetime

from pydantic import BaseModel


class ProjectRequest(BaseModel):
    title: str
    description: str | None = None

class ProjectAdd(ProjectRequest):
    owner_id: int

class Project(BaseModel):
    id: int
    title: str
    description: str | None = None
    owner_id: int
    created_at: datetime

class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
