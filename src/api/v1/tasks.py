from fastapi import APIRouter, HTTPException
from fastapi.params import Query
from fastapi_cache.decorator import cache
from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import CurrentUserIdDep, DBDep
from src.models import CategoryOrm, ProjectOrm, TaskOrm
from src.schemas.tasks import Task, TaskPUT, TaskRequest, TaskUpdate
from src.services.tasks import TaskService

router = APIRouter(prefix="/v1/tasks", tags=["Tasks"])


@router.get("", response_model=list[Task])
@cache(expire=15)
async def get_tasks(
        service: TaskService,
        user_id: CurrentUserIdDep,
        search: str | None = Query(None),
        status: str | None = Query(None)
):
    return await service.get_tasks(user_id, search, status)


@router.post("", response_model=Task)
async def create_task(service: TaskService, user_id: CurrentUserIdDep, data: TaskRequest):
    # try:
    return await service.create_task(user_id, data)

    # except IntegrityError:
    #     raise HTTPException(400, "Задача с таким названием уже существует")


@router.get("/{task_id}", response_model=Task)
@cache(expire=15)
async def get_task(task_id: int, service: TaskService, user_id: CurrentUserIdDep):
    return await service.get_task(task_id, user_id)


@router.put("/{task_id}", response_model=Task)
async def edit_task(task_id: int, data: TaskPUT, service: TaskService, user_id: CurrentUserIdDep):
    # try:
    return await service.edit_task(task_id, user_id, data)
    # except IntegrityError:
    #     raise HTTPException(400)


@router.patch("/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, service: TaskService, user_id: CurrentUserIdDep):
    # try:
    return await service.update_task(task_id, user_id, data)
    # except IntegrityError:
    #     raise HTTPException(400)


@router.delete("/{task_id}")
async def delete_task(task_id: int, service: TaskService, user_id: CurrentUserIdDep):
    # try:
    await service.delete_task(task_id, user_id)
    return {"status": True}
    # except: