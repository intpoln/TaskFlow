import logging

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError


class RedisManager:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self._redis: Redis | None = None
        self._connected = False

    async def connect(self):
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
        if not self._connected or not self._redis:
            return
        try:
            return await self._redis.get(key)
        except RedisConnectionError:
            self._connected = False

    async def delete(self, key: str):
        if not self._connected or not self._redis:
            return
        try:
            await self._redis.delete(key)
        except RedisConnectionError:
            self._connected = False

    async def close(self):
        await self._redis.close()
        self._connected = False
