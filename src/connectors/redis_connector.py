"""Коннектор для работы с Redis.

Предоставляет асинхронный клиент Redis с graceful degradation
при недоступности сервера.
"""

import logging

from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from src.core.exceptions import RedisConnectionError


class RedisManager:
    """Менеджер подключения к Redis.

    Обеспечивает отказоустойчивую работу с Redis:
    при недоступности сервера операции игнорируются
    вместо выброса исключений.

    Attributes:
        host: Хост Redis сервера.
        port: Порт Redis сервера.
        password: Пароль для аутентификации.

    Example:
        >>> redis = RedisManager("localhost", 6379, "password")
        >>> await redis.connect()
        >>> await redis.set("key", "value", expire=60)
        >>> value = await redis.get("key")
    """

    def __init__(self, host: str, port: int, password: str):
        """Инициализирует менеджер с параметрами подключения.

        Args:
            host: Хост Redis сервера.
            port: Порт Redis сервера.
            password: Пароль для аутентификации.
        """
        self.host = host
        self.port = port
        self.password = password
        self._redis: Redis | None = None
        self._connected = False

    async def connect(self):
        """Устанавливает подключение к Redis.

        При ошибке подключения логирует её и продолжает работу
        без Redis (graceful degradation).
        """
        try:
            logging.info(f"Начало подключения к Redis. host={self.host}, port={self.port}")
            self._redis = Redis(host=self.host, port=self.port, password=self.password)
            await self._redis.ping()
            self._connected = True
            logging.info(f"Подключение к Redis - успешно. host={self.host}, port={self.port}")
        except ConnectionError as ex:
            logging.error(
                f"Не удалось подключиться к Redis - {ex}. host={self.host}, port={self.port}"
            )
            self._connected = False
            self._redis = None
            raise RedisConnectionError

    async def set(self, key: str, value: str, expire: int = None):
        """Сохраняет значение по ключу.

        Args:
            key: Ключ для сохранения.
            value: Значение (строка).
            expire: Время жизни в секундах (опционально).
        """
        if not self._connected or not self._redis:
            return
        try:
            if expire:
                await self._redis.set(key, value, ex=expire)
            else:
                await self._redis.set(key, value)
        except ConnectionError:
            self._connected = False
            raise RedisConnectionError

    async def get(self, key: str):
        """Получает значение по ключу.

        Args:
            key: Ключ для получения.

        Returns:
            Значение или None если ключ не найден или Redis недоступен.
        """
        if not self._connected or not self._redis:
            return None
        try:
            return await self._redis.get(key)
        except ConnectionError:
            self._connected = False
            raise RedisConnectionError

    async def delete(self, key: str):
        """Удаляет ключ.

        Args:
            key: Ключ для удаления.
        """
        if not self._connected or not self._redis:
            return
        try:
            await self._redis.delete(key)
        except ConnectionError:
            self._connected = False
            raise RedisConnectionError

    async def close(self):
        """Закрывает подключение к Redis."""
        await self._redis.close()
        self._connected = False

    async def set_oauth_state(self, state: str, data: str = "pending", expire: int = 300):
        """Добавляет OAuth state с TTL 5 минут..

        Args:
            state: OAuth state.
            data: Любое значение (проверка будет по ключу).
            expire: Время жизни в секундах.
        """
        key = f"oauth_state:{state}"
        await self.set(key, data, expire)

    async def verify_oauth_state(self, state: str) -> bool:
        """Проверяет и удаляет OAuth state (one-time use).

        Returns:
            True или False если невалиден/истёк.
        """
        key = f"oauth_state:{state}"
        value = await self.get(key)

        if value:
            await self.delete(key)
            return True
        return False

    async def set_jwk(self, provider: str, jwk_data: str, expire: int = 86400):
        """Сохраняет JWK сертификаты провайдера.

        Args:
            provider: Название провайдера (google, github).
            jwk_data: JSON строка с JWK.
            expire: TTL в секундах (по умолчанию 1 день).
        """
        key = f"jwk:{provider}"
        await self.set(key, jwk_data, expire)

    async def get_jwk(self, provider: str) -> str | None:
        """Получает JWK сертификаты провайдера.

        Args:
            provider: Название провайдера.

        Returns:
            JSON строка с JWK или None.
        """
        key = f"jwk:{provider}"
        value = await self.get(key)
        if not value:
            return None
        return value
