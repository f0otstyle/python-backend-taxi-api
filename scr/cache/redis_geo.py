from redis.asyncio import Redis
from scr.core.config import settings


class RedisGeo:
    def __init__(self):
        self.redis = Redis.from_url(
            settings.DATABASE_URL_redis,
            decode_responses=True
        )
        self.key = "taxi:drivers:geo"

    async def add_geo_driver(self, driver_id: int, lat: float, lon: float):
        return await self.redis.geoadd(
            self.key,
            (lon, lat, f"drivers:{driver_id}")
            )

    async def remove_driver(self, driver_id: int):
        return await self.redis.zrem(self.key, f"drivers:{driver_id}")

    async def get_geo_search(self, lat: float, lon: float, radius: float):
        results = await self.redis.geosearch(
            name=self.key,
            longitude=lon,
            latitude=lat,
            radius=radius,
            unit="km",
            count=10,
            sort="ASC"
        )
        return [int(r.split(":")[1]) for r in results]
