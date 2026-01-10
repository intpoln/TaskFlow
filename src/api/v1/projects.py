from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import CurrentUserIdDep, DBDep
from src.models import ProjectOrm
from src.schemas.projects import Project, ProjectPUT, ProjectRequest, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[Project])
@cache(expire=15)
async def get_projects(db: DBDep, user_id: CurrentUserIdDep):
    query = select(ProjectOrm).filter_by(owner_id=user_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=Project)
async def create_project(db: DBDep, data: ProjectRequest, user_id: CurrentUserIdDep):
    try:
        add_stmt = (
            insert(ProjectOrm)
            .values(**data.model_dump(exclude_unset=True), owner_id=user_id)
            .returning(ProjectOrm)
        )
        result = await db.execute(add_stmt)
        project = result.scalar_one()
        await db.commit()
        return project
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Проект с таким названием уже существует")


@router.get("/{project_id}", response_model=Project)
@cache(expire=15)
async def get_project(project_id: int, db: DBDep, user_id: CurrentUserIdDep):
    query = select(ProjectOrm).filter_by(id=project_id, owner_id=user_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(404, "Проект не найден")

    return project


@router.put("/{project_id}", response_model=Project)
async def edit_project(project_id: int, data: ProjectPUT, db: DBDep, user_id: CurrentUserIdDep):
    try:
        edit_stmt = (
            update(ProjectOrm)
            .filter_by(id=project_id, owner_id=user_id)
            .values(**data.model_dump(), owner_id=user_id)
            .returning(ProjectOrm)
        )
        result = await db.execute(edit_stmt)
        await db.commit()
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(404, "Проект не найден")
        return project

    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Проект с таким названием уже существует")


@router.patch("/{project_id}")
async def update_project(
    project_id: int, data: ProjectUpdate, db: DBDep, user_id: CurrentUserIdDep
):
    try:
        edit_stmt = (
            update(ProjectOrm)
            .filter_by(id=project_id, owner_id=user_id)
            .values(**data.model_dump(exclude_unset=True), owner_id=user_id)
            .returning(ProjectOrm)
        )
        result = await db.execute(edit_stmt)
        await db.commit()
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(404, "Проект не найден")
        return project

    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Проект с таким названием уже существует")


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: DBDep, user_id: CurrentUserIdDep):
    query = select(ProjectOrm).filter_by(id=project_id, owner_id=user_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Проект не найден")
    try:
        del_stmt = delete(ProjectOrm).filter_by(id=project_id, owner_id=user_id)
        await db.execute(del_stmt)
        await db.commit()
        return {"status": True}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Нельзя удалить проект с существующими задачами")
