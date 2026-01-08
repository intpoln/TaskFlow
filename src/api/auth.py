from fastapi import APIRouter, HTTPException, Response, Request
from sqlalchemy import select, insert, or_

from src.api.dependencies import DBDep, CurrentUserDep
from src.config import settings
from src.models import UserOrm
from src.schemas.users import UserRegister, UserLogin, User
from src.services.auth import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register')
async def register(db: DBDep, data: UserRegister):
    query = select(UserOrm).filter(
        or_(
            UserOrm.email == data.email,
            UserOrm.username == data.username,
        )
    )
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.email == data.email:
            raise HTTPException(400, "Пользователь с таким email уже существует")
        raise HTTPException(400, "Пользователь с таким username уже существует")

    hashed_password = AuthService.hash_password(data.password)
    add_stmt = insert(UserOrm).values(
        email=data.email,
        username=data.username,
        hashed_password=hashed_password
    )

    await db.execute(add_stmt)
    await db.commit()
    return {'status': True, 'message': f'Пользователь {data.username} успешно зарегистрирован!'}

@router.post('/login')
async def login(db: DBDep, data: UserLogin, response: Response):
    query = select(UserOrm).filter_by(email=data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if not existing_user or not AuthService.verify_password(data.password, existing_user.hashed_password):
        raise HTTPException(400, 'Неверное сочетание почта/пароль')

    access_token = AuthService.create_access_token({"user_id": existing_user.id})
    response.set_cookie(key='access_token', value=access_token)

    refresh_token = AuthService.create_refresh_token({"user_id": existing_user.id})
    refresh_max_age = settings.REFRESH_TOKEN_COOKIE_MAX_AGE
    response.set_cookie(
            key='refresh_token', value=refresh_token, max_age=refresh_max_age, httponly=True
        )

    return {'status': True, 'message': 'Вы успешно вошли'}

@router.get('/me', response_model=User)
async def me(user: CurrentUserDep):
    return user


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')
    return {'status': True, 'message': 'Вы успешно вышли'}


@router.post('/refresh')
async def refresh_tokens(
        response: Response,
        request: Request,
):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPException(401, 'Refresh токен отсутствует')

    payload = AuthService.decode_refresh_token(refresh_token)

    if not payload:
        response.delete_cookie(key='refresh_token')
        response.delete_cookie(key='access_token')
        raise HTTPException(401, 'Refresh токен истёк, авторизуйтесь заново')

    user_id = payload.get('user_id')
    if not user_id:
        raise HTTPException(401, 'Невалидный refresh токен')

    new_access_token = AuthService.create_access_token({"user_id": user_id})
    response.set_cookie(key='access_token', value=new_access_token)

    new_refresh_token = AuthService.create_refresh_token({"user_id": user_id})
    refresh_max_age = settings.REFRESH_TOKEN_COOKIE_MAX_AGE
    response.set_cookie(
        key='refresh_token', value=new_refresh_token, max_age=refresh_max_age, httponly=True
    )

    return {"status": True, "message": "Токены обновлены!"}