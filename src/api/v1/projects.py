from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache

from src.api.dependencies import CurrentUserIdDep, ProjectServiceDep
from src.core.exceptions import ConflictError, NotFoundError
from src.schemas.projects import Project, ProjectPUT, ProjectRequest, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[Project])
@cache(expire=15)
async def get_projects(service: ProjectServiceDep, user_id: CurrentUserIdDep):
    return await service.get_projects(user_id)


@router.post("", response_model=Project)
async def create_project(
    service: ProjectServiceDep, data: ProjectRequest, user_id: CurrentUserIdDep
):
    try:
        return await service.create_project(data=data, user_id=user_id)
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.get("/{project_id}", response_model=Project)
@cache(expire=15)
async def get_project(project_id: int, service: ProjectServiceDep, user_id: CurrentUserIdDep):
    try:
        return await service.get_project(project_id, user_id)
    except NotFoundError as e:
        raise HTTPException(404, e.message)


@router.put("/{project_id}", response_model=Project)
async def edit_project(
    project_id: int, data: ProjectPUT, service: ProjectServiceDep, user_id: CurrentUserIdDep
):
    try:
        return await service.edit_project(data=data, user_id=user_id, project_id=project_id)
    except NotFoundError as e:
        raise HTTPException(404, e.message)
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.patch("/{project_id}", response_model=Project)
async def update_project(
    project_id: int, data: ProjectUpdate, service: ProjectServiceDep, user_id: CurrentUserIdDep
):
    try:
        return await service.update_project(data=data, user_id=user_id, project_id=project_id)
    except NotFoundError as e:
        raise HTTPException(404, e.message)
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.delete("/{project_id}")
async def delete_project(project_id: int, service: ProjectServiceDep, user_id: CurrentUserIdDep):
    try:
        await service.delete_project(project_id, user_id)
        return {"status": True}
    except NotFoundError as e:
        raise HTTPException(404, e.message)
