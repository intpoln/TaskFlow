"""API эндпоинты для задач.

Содержит CRUD эндпоинты для управления задачами пользователя.
"""

from fastapi import APIRouter, HTTPException
from fastapi.params import Query
from fastapi_cache.decorator import cache
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from src.api.dependencies import CurrentUserIdDep, TaskServiceDep
from src.core.exceptions import ConflictError, NotFoundError
from src.schemas.tasks import Task, TaskPUT, TaskRequest, TaskUpdate

router = APIRouter(prefix="/v1/tasks", tags=["Таски"])


@router.get("", response_model=list[Task], summary="Получение задач, удовлетворяющих поиску")
@cache(expire=60)
async def get_tasks(
    service: TaskServiceDep,
    user_id: CurrentUserIdDep,
    search: str | None = Query(
        None, description="Поиск по описанию задачи и названию задачи, проекта и категории"
    ),
    status: str | None = Query(None, description="Поиск по статусу"),
):
    """Получает список задач текущего пользователя.

    Поддерживает поиск и фильтрацию. Результат кэшируется на 15 секунд.

    Args:
        service: Сервис задач.
        user_id: ID текущего пользователя.
        search: Поисковый запрос (название, описание, проект, категория).
        status: Фильтр по статусу (TODO, IN_PROGRESS, DONE).

    Returns:
        Список задач, соответствующих критериям.
    """
    return await service.get_tasks(user_id, search, status)


@router.post("", response_model=Task, summary="Создание задачи", status_code=HTTP_201_CREATED)
async def create_task(service: TaskServiceDep, user_id: CurrentUserIdDep, data: TaskRequest):
    """Создает новую задачу.

    Проверяет существование проекта и категории.

    Args:
        service: Сервис задач.
        user_id: ID текущего пользователя.
        data: Данные для создания задачи.

    Returns:
        Созданная задача.

    Raises:
        HTTPException 404: Проект или категория не найдены.
        HTTPException 409: Задача с таким названием уже существует в проекте.
    """
    try:
        return await service.create_task(user_id, data)
    except ConflictError as ex:
        raise HTTPException(HTTP_409_CONFLICT, ex.message)
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)


@router.get("/{task_id}", response_model=Task, summary="Получение определенной задачи")
@cache(expire=60)
async def get_task(task_id: int, service: TaskServiceDep, user_id: CurrentUserIdDep):
    """Получает задачу по ID.

    Args:
        task_id: ID задачи.
        service: Сервис задач.
        user_id: ID текущего пользователя.

    Returns:
        Найденная задача.

    Raises:
        HTTPException 404: Задача не найдена.
    """
    try:
        return await service.get_task(task_id, user_id)
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)


@router.put("/{task_id}", response_model=Task, summary="Полная замена данных задачи")
async def edit_task(
    task_id: int, data: TaskPUT, service: TaskServiceDep, user_id: CurrentUserIdDep
):
    """Полностью обновляет задачу (PUT).

    Args:
        task_id: ID задачи.
        data: Полные новые данные задачи.
        service: Сервис задач.
        user_id: ID текущего пользователя.

    Returns:
        Обновленная задача.

    Raises:
        HTTPException 404: Задача, проект или категория не найдены.
        HTTPException 409: Задача с таким названием уже существует в проекте.
    """
    try:
        return await service.edit_task(task_id=task_id, user_id=user_id, data=data)
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)
    except ConflictError as ex:
        raise HTTPException(HTTP_409_CONFLICT, ex.message)


@router.patch("/{task_id}", response_model=Task, summary="Частичное обновление данных задачи")
async def update_task(
    task_id: int, data: TaskUpdate, service: TaskServiceDep, user_id: CurrentUserIdDep
):
    """Частично обновляет задачу (PATCH).

    Args:
        task_id: ID задачи.
        data: Частичные данные для обновления.
        service: Сервис задач.
        user_id: ID текущего пользователя.

    Returns:
        Обновленная задача.

    Raises:
        HTTPException 404: Задача не найдена.
        HTTPException 409: Задача с таким названием уже существует в проекте.
    """
    try:
        return await service.update_task(task_id=task_id, user_id=user_id, data=data)
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)
    except ConflictError as ex:
        raise HTTPException(HTTP_409_CONFLICT, ex.message)


@router.delete("/{task_id}", summary="Удаление задачи")
async def delete_task(task_id: int, service: TaskServiceDep, user_id: CurrentUserIdDep):
    """Удаляет задачу.

    Args:
        task_id: ID задачи.
        service: Сервис задач.
        user_id: ID текущего пользователя.

    Returns:
        Результат удаления.

    Raises:
        HTTPException 404: Задача не найдена.
    """
    try:
        await service.delete_task(task_id, user_id)
        return {"status": True}
    except NotFoundError as ex:
        raise HTTPException(HTTP_404_NOT_FOUND, ex.message)
