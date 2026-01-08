from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import DBDep, CurrentUserIdDep
from src.models import TaskOrm, ProjectOrm
from src.schemas.tasks import Task, TaskRequest

router = APIRouter(prefix='/tasks', tags=['Tasks'])


@router.get('', response_model=list[Task])
@cache(expire=15)
async def get_tasks(db: DBDep, user_id: CurrentUserIdDep):
    query = select(TaskOrm).filter_by(owner_id=user_id)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@router.post('', response_model=Task)
async def create_task(db: DBDep, user_id: CurrentUserIdDep, data: TaskRequest):
    try:
        query = select(ProjectOrm).filter_by(id=data.project_id, owner_id=user_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(404, 'Такого проекта не существует')

        add_stmt = insert(TaskOrm).values(**data.model_dump(exclude_unset=True), owner_id = user_id).returning(TaskOrm)
        result = await db.execute(add_stmt)
        await db.commit()
        task = result.scalar_one()
        return task

    except IntegrityError:
        HTTPException(400, 'Задача с таким названием уже существует')


@router.get('/{task_id}', response_model=Task)
@cache(expire=15)
async def get_task(task_id: int, db: DBDep, user_id: CurrentUserIdDep):
    query = select(TaskOrm).filter_by(id=task_id, owner_id=user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        HTTPException(404, 'Такой задачи не существует')

    return task