from src.core.exceptions import ConflictError, NotFoundError
from src.schemas.projects import Project, ProjectPUT, ProjectRequest, ProjectUpdate
from src.services.base import BaseService


class ProjectService(BaseService):
    async def get_projects(self, user_id) -> list[Project]:
        return await self.db.projects.get_filtered(owner_id=user_id)

    async def get_project(self, project_id, user_id) -> Project:
        try:
            return await self.db.projects.get_filtered_one(owner_id=user_id, id=project_id)
        except NotFoundError:
            raise NotFoundError(f"Проект с id {project_id} не найден")

    async def create_project(self, user_id: int, data: ProjectRequest) -> Project:
        try:
            project = await self.db.projects.create(data={**data.model_dump(), "owner_id": user_id})
            await self.db.commit()
            return project
        except ConflictError:
            raise ConflictError(f"Проект с названием {data.title} уже существует")

    async def edit_project(self, project_id: int, user_id: int, data: ProjectPUT) -> Project:
        try:
            await self.check_project_exists(project_id, user_id)
            project = await self.db.projects.update(
                data={**data.model_dump(), "owner_id": user_id}, id=project_id
            )
            await self.db.commit()
            return project
        except ConflictError:
            raise ConflictError(f"Проект с названием {data.title} уже существует")

    async def update_project(self, project_id: int, user_id: int, data: ProjectUpdate) -> Project:
        try:
            await self.check_project_exists(project_id, user_id)
            project = await self.db.projects.update(
                data={**data.model_dump(exclude_unset=True), "owner_id": user_id}, id=project_id
            )
            await self.db.commit()
            return project
        except ConflictError:
            raise ConflictError(f"Проект с названием {data.title} уже существует")

    async def delete_project(self, project_id: int, user_id: int) -> None:
        await self.check_project_exists(project_id, user_id)
        await self.db.projects.delete(project_id)
        await self.db.commit()
