from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.api.dependencies import ProjectServiceDep, CurrentUserIdDep
from src.schemas.projects import Project, ProjectPUT, ProjectRequest, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[Project])
@cache(expire=15)
async def get_projects(service: ProjectServiceDep, user_id: CurrentUserIdDep):
    return await service.get_projects(user_id)


@router.post("", response_model=Project)
async def create_project(service: ProjectServiceDep, data: ProjectRequest, user_id: CurrentUserIdDep):
    # try:
    return await service.create_project(data=data, user_id=user_id)
    # except IntegrityError:


@router.get("/{project_id}", response_model=Project)
@cache(expire=15)
async def get_project(project_id: int, service: ProjectServiceDep, user_id: CurrentUserIdDep):
    # try:
    return await service.get_project(project_id, user_id)
    # except NotFoundError:


@router.put("/{project_id}", response_model=Project)
async def edit_project(
    project_id: int, data: ProjectPUT, service: ProjectServiceDep, user_id: CurrentUserIdDep
):
    # try:
    return await service.edit_project(data=data, user_id=user_id, project_id=project_id)
    # except:


@router.patch("/{project_id}", response_model=Project)
async def update_project(
    project_id: int, data: ProjectUpdate, service: ProjectServiceDep, user_id: CurrentUserIdDep
):
    # try:
    return await service.update_project(data=data, user_id=user_id, project_id=project_id)
    # except:


@router.delete("/{project_id}")
async def delete_project(project_id: int, service: ProjectServiceDep, user_id: CurrentUserIdDep):
    await service.delete_project(project_id, user_id)
    return {"status": True}
