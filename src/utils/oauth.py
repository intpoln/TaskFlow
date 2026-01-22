import json
import re

import httpx

from src.config import settings
from src.core.exceptions import ExternalServiceError
from src.init import redis_manager


async def fetch_google_jwks() -> dict:
    """Асинхронно загружает JWK сертификаты от Google.

    Парсит заголовок Cache-Control для определения TTL кеша.

    Returns:
        Словарь с ключами 'jwks' и 'max_age'.

    Raises:
        ExternalServiceError: При ошибке HTTP запроса.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.GOOGLE_JWK_URI, timeout=20)
            response.raise_for_status()
            jwks = response.json()

            jwks = response.json()
            max_age = _parse_cache_max_age(response.headers.get("Cache-Control"))

            return {"jwks": jwks, "max_age": max_age}
    except httpx.HTTPStatusError as ex:
        raise ExternalServiceError(f"Ошибка получения сертификатов Google: {ex.response.json()}")
    except httpx.RequestError:
        raise ExternalServiceError("Не удалось подключиться к серверу Google")


async def get_google_jwks() -> dict:
    """Получает JWK сертификаты Google с кешированием в Redis.

    Сначала проверяет кеш, при отсутствии — загружает и кеширует.

    Returns:
        Словарь с JWK ключами (формат JWKS).

    Raises:
        ExternalServiceError: При ошибке загрузки и отсутствии кеша.
    """
    cached_jwk = await redis_manager.get_jwk("google")

    if cached_jwk:
        try:
            return json.loads(cached_jwk)
        except json.JSONDecodeError:
            pass

    jwks_data = await fetch_google_jwks()
    jwks = jwks_data["jwks"]
    max_age = jwks_data.get("max_age")

    await redis_manager.set_jwk("google", json.dumps(jwks), expire=max_age or 3600)

    return jwks


def _parse_cache_max_age(cache_control: str | None) -> int | None:
    """Парсит max-age из заголовка Cache-Control.

    Args:
        cache_control: Значение заголовка Cache-Control.

    Returns:
        Значение max-age в секундах или None.
    """
    if not cache_control:
        return None
    match = re.search(r"max-age=(\d+)", cache_control)
    return int(match.group(1)) if match else None
