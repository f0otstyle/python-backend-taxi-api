from random import randint
from time import time

from redis.asyncio import Redis
from scr.core.config import settings
import json


class RedisCachedBackend:
    def __init__(self, cache_ttl_seconds: int | None):
        self.redis = Redis.from_url(
            settings.DATABASE_URL_redis,
            decode_responses=True
            )
        self.cache_ttl_seconds = cache_ttl_seconds
        self.prefix = 'taxi'

    def _make_key(self, entity: str, identifier: str) -> str:
        return f'{self.prefix}:{entity}:{identifier}'

    async def get(self,
                  entity: str,
                  identifier: str
                  ) -> dict | list[dict] | None:
        key = self._make_key(entity, identifier)
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self,
                  entity: str,
                  identifier: str,
                  value: dict | list[dict]
                  ):
        key = self._make_key(entity=entity, identifier=identifier)
        await self.redis.set(key, json.dumps(value), ex=self.cache_ttl_seconds)

    async def delete(self, entity: str, identifier: str):
        key = self._make_key(entity=entity, identifier=identifier)
        await self.redis.delete(key)

    async def close(self):
        await self.redis.close()


class Ratelimit:
    def __init__(self):
        self.redis = Redis.from_url(
                    settings.DATABASE_URL_redis,
                    decode_responses=True
                )
        self.prefix = 'rate_limite'

    def _make_key(self, entity: str, identifier: str | int) -> str:
        return f'{self.prefix}:{entity}:{identifier}'

    async def is_limited(
            self,
            identifier: str | int,
            endpoint: str,
            max_request: int,
            window_seconds: int
    ):
        key = self._make_key(entity=endpoint, identifier=identifier)

        current_ms = time() * 1000

        window_start_ms = current_ms - window_seconds * 1000

        current_request = f"{time() * 1000}-{randint(0, 100_000)}"

        async with self.redis.pipeline() as pipe:
            await pipe.zremrangebyscore(key, 0, window_start_ms)

            await pipe.zcard(key)

            await pipe.zadd(key, {current_request: current_ms})

            await pipe.expire(key, window_seconds)

            res = await pipe.execute()

        _, current_count, _, _ = res
        if current_count >= max_request:
            return True
