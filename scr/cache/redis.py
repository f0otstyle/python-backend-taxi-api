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
