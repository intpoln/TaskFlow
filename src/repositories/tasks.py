from sqlalchemy import or_, select

from src.models import CategoryOrm, ProjectOrm, TaskOrm
from src.repositories.base import BaseRepository


class TaskRepository(BaseRepository):
    model = TaskOrm

    async def get_user_tasks(
        self, user_id: int, search: str | None = None, status: str | None = None
    ) -> list[TaskOrm]:
        query = select(self.model).filter_by(owner_id=user_id)

        if search:
            pattern = f"%{search}%"
            query = query.outerjoin(ProjectOrm).outerjoin(CategoryOrm)
            query = query.where(
                or_(
                    self.model.title.ilike(pattern),
                    self.model.description.ilike(pattern),
                    ProjectOrm.title.ilike(pattern),
                    CategoryOrm.title.ilike(pattern),
                )
            )

        if status:
            query = query.where(self.model.status == status)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_task(self, task_id: int, user_id: int) -> TaskOrm:
        query = select(self.model).filter_by(id=task_id, owner_id=user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
