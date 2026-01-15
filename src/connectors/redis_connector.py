"""Коннектор для работы с Redis.

Предоставляет асинхронный клиент Redis с graceful degradation
при недоступности сервера.
"""

import logging

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError


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
        except RedisConnectionError as e:
            logging.error(
                f"Не удалось подключиться к Redis - {e}. host={self.host}, port={self.port}"
            )
            self._connected = False
            self._redis = None

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
        except RedisConnectionError:
            self._connected = False

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
        except RedisConnectionError:
            self._connected = False

    async def delete(self, key: str):
        """Удаляет ключ.

        Args:
            key: Ключ для удаления.
        """
        if not self._connected or not self._redis:
            return
        try:
            await self._redis.delete(key)
        except RedisConnectionError:
            self._connected = False

    async def close(self):
        """Закрывает подключение к Redis."""
        await self._redis.close()
        self._connected = False
