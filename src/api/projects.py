from fastapi import APIRouter, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import DBDep, CurrentUserIdDep
from src.models import ProjectOrm
from src.schemas.projects import Project, ProjectRequest

router = APIRouter(prefix='/projects', tags=['projects'])


@router.get('', response_model=list[Project])
async def get_projects(db: DBDep, user_id: CurrentUserIdDep):
    query = select(ProjectOrm).filter_by(owner_id=user_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post('', response_model=Project)
async def create_project(db: DBDep, data: ProjectRequest, user_id: CurrentUserIdDep):

    try:
        add_stmt = insert(ProjectOrm).values(**data.model_dump(exclude_unset=True), owner_id=user_id).returning(ProjectOrm)
        result = await db.execute(add_stmt)
        project = result.scalar_one()
        await db.commit()
        return project
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, 'Проект с таким названием уже существует')