"""API эндпоинты для OAuth 2.0 аутентификации.

Содержит эндпоинты для авторизации через внешних провайдеров (Google).
"""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND, HTTP_503_SERVICE_UNAVAILABLE

from src.api.dependencies import AuthServiceDep
from src.config import settings
from src.core.exceptions import (
    ExternalServiceError,
    ForbiddenError,
    NotAuthorizedError,
    RedisConnectionError,
)

router = APIRouter(prefix="/oauth", tags=["OAuth 2.0"])


@router.get(
    "/google",
    summary="Авторизация через Google OAuth 2.0",
    description="Возвращает ссылку для авторизации с помощью Google "
    "OAuth, перейдите на нее для начала авторизации",
)
async def redirect_to_google_oauth(service: AuthServiceDep):
    """Инициирует OAuth flow с Google."""
    try:
        redirect_url = await service.generate_google_oauth_redirect_uri()
        return {"redirect_url": redirect_url}
    except RedisConnectionError:
        raise HTTPException(
            HTTP_503_SERVICE_UNAVAILABLE, "Внутренняя ошибка сервиса. Попробуйте позже."
        )


@router.get("/google/callback", include_in_schema=False)
async def google_oauth_callback(
    code: str,
    state: str | None,
    request: Request,
    service: AuthServiceDep,
    user_agent: Annotated[str | None, Header(include_in_schema=False)] = None,
):
    """Callback от Google после авторизации пользователем."""
    try:
        tokens = await service.authenticate_google_user(
            code=code, state=state, fingerprint=user_agent
        )
    except ForbiddenError as ex:
        raise HTTPException(403, ex.message)
    except NotAuthorizedError as ex:
        raise HTTPException(401, ex.message)
    except ExternalServiceError as ex:
        raise HTTPException(502, ex.message)
    except RedisConnectionError:
        raise HTTPException(503, "Сервис временно недоступен")

    response = RedirectResponse(request.url_for("root"), status_code=HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        max_age=settings.REFRESH_TOKEN_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )

    return response
