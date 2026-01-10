from src.schemas.projects import ProjectRequest, Project
from src.services.base import BaseService


class ProjectService(BaseService):

    async def get_projects(self, user_id) -> list[Project]:
        return await self.db.projects.get_filtered(owner_id=user_id)


    async def get_project(self, project_id, user_id) -> Project:
        return await self.db.projects.get_filtered(owner_id=user_id, project_id=project_id)


    async def create_project(self, data: ProjectRequest) -> Project:
        project = await self.db.projects.create(data=data)
        await self.db.commit()
        return project

    async def edit_project(self, project_id: int, user_id: int, data: Project) -> Project:
        await self.check_project_exists(project_id, user_id)
        project = await self.db.projects.update({**data.model_dump(), "owner_id": user_id})
        await self.db.commit()
        return project

    async def update_project(self, project_id: int, user_id: int, data: Project) -> Project:
        await self.check_project_exists(project_id, user_id)
        project = await self.db.projects.update({**data.model_dump(exclude_unset=True), "project_id": project_id})
        await self.db.commit()
        return project

    async def delete_project(self, project_id: int, user_id: int) -> None:
        await self.check_project_exists(project_id, user_id)
        await self.db.projects.delete(project_id)
        await self.db.commit()