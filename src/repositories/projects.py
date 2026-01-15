from sqlalchemy import select

from src.core.exceptions import NotFoundError
from src.models import ProjectOrm
from src.repositories.base import BaseRepository
from src.schemas.projects import Project


class ProjectRepository(BaseRepository):
    model = ProjectOrm

    async def get_user_project(self, project_id: int, user_id: int) -> Project:
        query = select(ProjectOrm).filter_by(id=project_id, owner_id=user_id)
        result = await self.session.execute(query)
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundError(f"Проект с id {project_id} не найден")
        return project
