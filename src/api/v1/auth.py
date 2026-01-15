from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, Response

from src.api.dependencies import AuthServiceDep, CurrentUserDep
from src.config import settings
from src.core.exceptions import ConflictError, ForbiddenError, NotAuthorizedError
from src.schemas.users import User, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


def set_auth_tokens(response: Response, tokens: dict):
    response.set_cookie(key="access_token", value=tokens["access_token"])
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        max_age=settings.REFRESH_TOKEN_COOKIE_MAX_AGE,
        httponly=True,
    )


@router.post("/register")
async def register(service: AuthServiceDep, data: UserRegister):
    try:
        return await service.register(data)
    except ConflictError as e:
        raise HTTPException(409, e.message)


@router.post("/login")
async def login(
    service: AuthServiceDep,
    data: UserLogin,
    response: Response,
    user_agent: Annotated[str | None, Header(include_in_schema=False)] = None,
):
    try:
        tokens = await service.create_tokens(data, fingerprint=user_agent)
        set_auth_tokens(response, tokens)
        return {"status": True, "message": "Вы успешно вошли"}
    except ForbiddenError as e:
        raise HTTPException(401, e.message)


@router.get("/me", response_model=User)
async def me(user: CurrentUserDep):
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"status": True, "message": "Вы успешно вышли"}


@router.post("/refresh")
async def refresh_tokens(
    service: AuthServiceDep,
    response: Response,
    request: Request,
    user_agent: Annotated[str | None, Header(include_in_schema=False)] = None,
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(401, "Refresh токен отсутствует")

    try:
        tokens = await service.refresh(refresh_token, fingerprint=user_agent)
        set_auth_tokens(response, tokens)
        return {"status": True, "message": "Токены обновлены!"}
    except NotAuthorizedError as e:
        raise HTTPException(401, e.message)
