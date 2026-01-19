"""API эндпоинты аутентификации.

Содержит эндпоинты для регистрации, авторизации,
выхода и обновления токенов.
"""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, Response
from fastapi_cache.decorator import cache
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

from src.api.dependencies import AuthServiceDep, CurrentUserDep
from src.config import settings
from src.core.exceptions import ConflictError, ForbiddenError, NotAuthorizedError
from src.schemas.users import User, UserLogin, UserRegister

router = APIRouter(prefix="/v1/auth", tags=["Аутентификация"])


def set_auth_tokens(response: Response, tokens: dict):
    """Устанавливает токены в cookies ответа.

    Args:
        response: HTTP ответ FastAPI.
        tokens: Словарь с access_token и refresh_token.
    """
    response.set_cookie(key="access_token", value=tokens["access_token"])
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        max_age=settings.REFRESH_TOKEN_COOKIE_MAX_AGE,
        httponly=True,
    )


@router.post("/register", summary="Регистрация пользователя", status_code=HTTP_201_CREATED)
async def register(service: AuthServiceDep, data: UserRegister):
    """Регистрирует нового пользователя.

    Args:
        service: Сервис аутентификации.
        data: Данные для регистрации (email, password, username).

    Returns:
        Результат регистрации с сообщением.

    Raises:
        HTTPException 409: Email или username уже заняты.
    """
    try:
        return await service.register(data)
    except ConflictError as e:
        raise HTTPException(HTTP_409_CONFLICT, e.message)


@router.post("/login", summary="Аутентификация пользователя")
async def login(
    service: AuthServiceDep,
    data: UserLogin,
    response: Response,
    user_agent: Annotated[str | None, Header(include_in_schema=False)] = None,
):
    """Авторизует пользователя и устанавливает токены.

    Args:
        service: Сервис аутентификации.
        data: Данные для входа (email, password).
        response: HTTP ответ для установки cookies.
        user_agent: User-Agent браузера для fingerprint.

    Returns:
        Результат авторизации.

    Raises:
        HTTPException 401: Неверный email или пароль.
    """
    try:
        tokens = await service.create_tokens(data, fingerprint=user_agent)
        set_auth_tokens(response, tokens)
        return {"status": True, "message": "Вы успешно вошли"}
    except ForbiddenError as e:
        raise HTTPException(HTTP_401_UNAUTHORIZED, e.message)


@router.get("/me", response_model=User, summary="Получение данных пользователя")
@cache(expire=60)
async def me(user: CurrentUserDep):
    """Возвращает данные текущего пользователя.

    Args:
        user: Текущий авторизованный пользователь.

    Returns:
        Данные пользователя.
    """
    return user


@router.post("/logout", summary="Выйти из аккаунта")
async def logout(response: Response):
    """Выходит из системы, удаляя токены.

    Args:
        response: HTTP ответ для удаления cookies.

    Returns:
        Результат выхода.
    """
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"status": True, "message": "Вы успешно вышли"}


@router.post("/refresh", summary="Обновление токенов")
async def refresh_tokens(
    service: AuthServiceDep,
    response: Response,
    request: Request,
    user_agent: Annotated[str | None, Header(include_in_schema=False)] = None,
):
    """Обновляет токены по refresh токену.

    Реализует token rotation - при каждом обновлении
    выдаётся новая пара токенов.

    Args:
        service: Сервис аутентификации.
        response: HTTP ответ для установки новых cookies.
        request: HTTP запрос для получения refresh токена.
        user_agent: User-Agent для верификации fingerprint.

    Returns:
        Результат обновления токенов.

    Raises:
        HTTPException 401: Refresh токен отсутствует, истёк или невалиден.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(HTTP_401_UNAUTHORIZED, "Refresh токен отсутствует")

    try:
        tokens = await service.refresh(refresh_token, fingerprint=user_agent)
        set_auth_tokens(response, tokens)
        return {"status": True, "message": "Токены обновлены!"}
    except NotAuthorizedError as e:
        raise HTTPException(HTTP_401_UNAUTHORIZED, e.message)
