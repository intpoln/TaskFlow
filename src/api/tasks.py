from fastapi import APIRouter, HTTPException
from fastapi.params import Query
from fastapi_cache.decorator import cache
from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import CurrentUserIdDep, DBDep
from src.models import CategoryOrm, ProjectOrm, TaskOrm
from src.schemas.tasks import Task, TaskPUT, TaskRequest, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=list[Task])
@cache(expire=15)
async def get_tasks(db: DBDep, user_id: CurrentUserIdDep, search: str | None = Query(None)):
    query = select(TaskOrm).filter_by(owner_id=user_id)
    if search:
        search_pattern = f"%{search}%"

        query = query.outerjoin(ProjectOrm, TaskOrm.project_id == ProjectOrm.id)
        query = query.outerjoin(CategoryOrm, TaskOrm.category_id == CategoryOrm.id)

        query = query.where(
            or_(
                TaskOrm.title.ilike(search_pattern),
                TaskOrm.description.ilike(search_pattern),
                CategoryOrm.title.ilike(search_pattern),
                ProjectOrm.title.ilike(search_pattern),
            )
        )

    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@router.post("", response_model=Task)
async def create_task(db: DBDep, user_id: CurrentUserIdDep, data: TaskRequest):
    try:
        query = select(ProjectOrm).filter_by(id=data.project_id, owner_id=user_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(404, "Проект не найден")

        add_stmt = (
            insert(TaskOrm)
            .values(**data.model_dump(exclude_unset=True), owner_id=user_id)
            .returning(TaskOrm)
        )
        result = await db.execute(add_stmt)
        await db.commit()
        task = result.scalar_one()
        return task

    except IntegrityError:
        raise HTTPException(400, "Задача с таким названием уже существует")


@router.get("/{task_id}", response_model=Task)
@cache(expire=15)
async def get_task(task_id: int, db: DBDep, user_id: CurrentUserIdDep):
    query = select(TaskOrm).filter_by(id=task_id, owner_id=user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Задача не найдена")

    return task


@router.put("/{task_id}", response_model=Task)
async def edit_task(task_id: int, data: TaskPUT, db: DBDep, user_id: CurrentUserIdDep):
    try:
        edit_stmt = (
            update(TaskOrm)
            .filter_by(id=task_id, owner_id=user_id)
            .values(**data.model_dump(), owner_id=user_id)
            .returning(TaskOrm)
        )
        result = await db.execute(edit_stmt)
        await db.commit()
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(404, "Задача не найдена")
        return task
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400)


@router.patch("/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, db: DBDep, user_id: CurrentUserIdDep):
    try:
        update_stmt = (
            update(TaskOrm)
            .filter_by(id=task_id, owner_id=user_id)
            .values(**data.model_dump(exclude_unset=True), owner_id=user_id)
            .returning(TaskOrm)
        )
        result = await db.execute(update_stmt)
        await db.commit()
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(404, "Задача не найдена")
        return task
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400)


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: DBDep, user_id: CurrentUserIdDep):
    query = select(TaskOrm).filter_by(id=task_id, owner_id=user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Задача не найдена")

    del_stmt = delete(TaskOrm).filter_by(id=task_id, owner_id=user_id)
    await db.execute(del_stmt)
    await db.commit()
    return {"status": True}
