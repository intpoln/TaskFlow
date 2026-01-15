from fastapi import APIRouter, HTTPException
from fastapi.params import Query
from fastapi_cache.decorator import cache

from src.api.dependencies import CurrentUserIdDep, TaskServiceDep
from src.core.exceptions import ConflictError, NotFoundError
from src.schemas.tasks import Task, TaskPUT, TaskRequest, TaskUpdate

router = APIRouter(prefix="/v1/tasks", tags=["Tasks"])


@router.get("", response_model=list[Task])
@cache(expire=15)
async def get_tasks(
    service: TaskServiceDep,
    user_id: CurrentUserIdDep,
    search: str | None = Query(None),
    status: str | None = Query(None),
):
    return await service.get_tasks(user_id, search, status)


@router.post("", response_model=Task)
async def create_task(service: TaskServiceDep, user_id: CurrentUserIdDep, data: TaskRequest):
    try:
        return await service.create_task(user_id, data)
    except ConflictError as e:
        raise HTTPException(409, e.message)
    except NotFoundError as e:
        raise HTTPException(404, e.message)


@router.get("/{task_id}", response_model=Task)
@cache(expire=15)
async def get_task(task_id: int, service: TaskServiceDep, user_id: CurrentUserIdDep):
    try:
        return await service.get_task(task_id, user_id)
    except NotFoundError as e:
        raise HTTPException(404, e.message)


@router.put("/{task_id}", response_model=Task)
async def edit_task(
    task_id: int, data: TaskPUT, service: TaskServiceDep, user_id: CurrentUserIdDep
):
    try:
        return await service.edit_task(task_id=task_id, user_id=user_id, data=data)
    except NotFoundError as e:
        raise HTTPException(404, e.message)
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.patch("/{task_id}", response_model=Task)
async def update_task(
    task_id: int, data: TaskUpdate, service: TaskServiceDep, user_id: CurrentUserIdDep
):
    try:
        return await service.update_task(task_id=task_id, user_id=user_id, data=data)
    except NotFoundError as e:
        raise HTTPException(404, e.message)
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.delete("/{task_id}")
async def delete_task(task_id: int, service: TaskServiceDep, user_id: CurrentUserIdDep):
    try:
        await service.delete_task(task_id, user_id)
        return {"status": True}
    except NotFoundError as e:
        raise HTTPException(404, e.message)
