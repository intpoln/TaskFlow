"""API эндпоинты для проектов.

Содержит CRUD эндпоинты для управления проектами пользователя.
"""

from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from src.api.dependencies import CurrentUserIdDep, ProjectServiceDep
from src.core.exceptions import ConflictError, NotFoundError
from src.schemas.projects import Project, ProjectPUT, ProjectRequest, ProjectUpdate

router = APIRouter(prefix="/v1/projects", tags=["Проекты"])


@router.get("", response_model=list[Project], summary="Получение всех проектов")
@cache(expire=60)
async def get_projects(service: ProjectServiceDep, user_id: CurrentUserIdDep):
    """Получает список проектов текущего пользователя.

    Результат кэшируется на 60 секунд.

    Args:
        service: Сервис проектов.
        user_id: ID текущего пользователя.

    Returns:
        Список проектов пользователя.
    """
    return await service.get_projects(user_id)


@router.post("", response_model=Project, summary="Создание проекта", status_code=HTTP_201_CREATED)
async def create_project(
    service: ProjectServiceDep, data: ProjectRequest, user_id: CurrentUserIdDep
):
    """Создает новый проект.

    Args:
        service: Сервис проектов.
        data: Данные для создания проекта.
        user_id: ID текущего пользователя.

    Returns:
        Созданный проект.

    Raises:
        HTTPException 409: Проект с таким названием уже существует.
    """
    try:
        return await service.create_project(data=data, user_id=user_id)
    except ConflictError as ex:
        raise HTTPException(HTTP_409_CONFLICT, ex.message)


@router.get("/{project_id}", response_model=Project, summary="Получение определенного проекта")
@cache(expire=60)
async def get_project(project_id: int, service: ProjectServiceDep, user_id: CurrentUserIdDep):
    """Получает проект по ID.

    Args:
        project_id: ID проекта.
        service: Сервис проектов.
        user_id: ID текущего пользователя.

    Returns:
        Найденный проект.

    Raises:
        HTTPException 404: Проект не найден.
    """
    try:
        return await service.get_project(project_id, user_id)
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)


@router.put("/{project_id}", response_model=Project, summary="Полное обновление проекта")
async def edit_project(
    project_id: int, data: ProjectPUT, service: ProjectServiceDep, user_id: CurrentUserIdDep
):
    """Полностью обновляет проект (PUT).

    Args:
        project_id: ID проекта.
        data: Полные новые данные проекта.
        service: Сервис проектов.
        user_id: ID текущего пользователя.

    Returns:
        Обновленный проект.

    Raises:
        HTTPException 404: Проект не найден.
        HTTPException 409: Проект с таким названием уже существует.
    """
    try:
        return await service.edit_project(data=data, user_id=user_id, project_id=project_id)
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)
    except ConflictError as ex:
        raise HTTPException(HTTP_409_CONFLICT, ex.message)


@router.patch("/{project_id}", response_model=Project, summary="Частичное обновление проекта")
async def update_project(
    project_id: int, data: ProjectUpdate, service: ProjectServiceDep, user_id: CurrentUserIdDep
):
    """Частично обновляет проект (PATCH).

    Args:
        project_id: ID проекта.
        data: Частичные данные для обновления.
        service: Сервис проектов.
        user_id: ID текущего пользователя.

    Returns:
        Обновленный проект.

    Raises:
        HTTPException 404: Проект не найден.
        HTTPException 409: Проект с таким названием уже существует.
    """
    try:
        return await service.update_project(data=data, user_id=user_id, project_id=project_id)
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)
    except ConflictError as ex:
        raise HTTPException(HTTP_409_CONFLICT, ex.message)


@router.delete("/{project_id}", summary="Удаление проекта")
async def delete_project(project_id: int, service: ProjectServiceDep, user_id: CurrentUserIdDep):
    """Удаляет проект.

    Все задачи проекта будут удалены каскадно.

    Args:
        project_id: ID проекта.
        service: Сервис проектов.
        user_id: ID текущего пользователя.

    Returns:
        Результат удаления.

    Raises:
        HTTPException 404: Проект не найден.
    """
    try:
        await service.delete_project(project_id, user_id)
        return {"status": True}
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)
