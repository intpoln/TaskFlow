from src.schemas.tasks import Task, TaskRequest, TaskPUT, TaskUpdate
from src.services.base import BaseService
from src.core.exceptions import NotFoundError


class TaskService(BaseService):

    async def get_tasks(
            self, user_id: int,
            search: str | None = None,
            status: str | None = None
    ) -> list[Task]:
        return await self.db.tasks.get_user_tasks(user_id=user_id, search=search, status=status)

    async def get_task(self, task_id: int, user_id) -> Task:
        return await self.db.get_user_task(task_id=task_id, user_id=user_id)

    async def create_task(self, user_id: int, data: TaskRequest) -> Task:
        project = await self.db.projects.get_by_id(data.project_id)

        if not project:
            raise NotFoundError("Проект не найден")

        if data.category_id:
            category = await self.db.categories.get_by_id(data.category_id)
            if not category:
                raise NotFoundError('Категория не найдена')

        task = await self.db.tasks.create({
            **data.model_dump(exclude_unset=True),
            "owner_id": user_id,
        })
        await self.db.commit()
        return task

    async def edit_task(self, task_id: int, user_id: int, data: TaskPUT) -> Task:
        pass

    async def update_task(self, task_id: int, user_id: int, data: TaskUpdate) -> Task:
        pass

    async def delete_task(self, task_id: int, user_id: int) -> None:
        pass