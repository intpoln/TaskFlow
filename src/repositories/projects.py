from sqlalchemy import select

from src.models import ProjectOrm
from src.repositories.base import BaseRepository
from src.schemas.projects import Project


class ProjectRepository(BaseRepository):
    model = ProjectOrm

    async def get_user_project(self, project_id: int, user_id: int) -> Project:
        query = select(ProjectOrm).filter_by(project_id=project_id, owner_id=user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()