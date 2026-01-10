from src.utils.db_manager import DBManager
from src.core.exceptions import NotFoundError

class BaseService:
    db: DBManager

    def __init__(self, db: DBManager):
        self.db = db


    async def check_project_exists(self, project_id: int, user_id: int) -> bool:
        project = await self.db.projects.get_user_project(project_id, user_id)

        if not project:
            raise NotFoundError("Проект не найден")

        return True

    async def check_category_exists(self, category_id: int) -> bool:
        category = await self.db.categories.get_by_id(category_id)

        if not category:
            raise NotFoundError('Категория не найдена')

        return True

    async def check_task_exists(self, task_id: int, user_id: int) -> bool:
        task = await self.db.tasks.get_user_task(task_id=task_id, user_id=user_id)

        if not task:
            raise NotFoundError('Задача не найдена')

        return True

    async def check_project_category_exists(
            self,
            project_id: int,
            user_id: int,
            category_id: int
    ) -> bool:
        project = await self.check_project_exists(project_id, user_id)
        category = await self.check_category_exists(category_id)
        return project and category