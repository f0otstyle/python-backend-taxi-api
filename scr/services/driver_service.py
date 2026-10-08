from sqlalchemy.ext.asyncio import AsyncSession
from error_handler import SearchError
from scr.repositories.driver_repositories import DriversRepository
from scr.schemas.driver_schemas import (DriverCreate,
                                        DriverResponseSchema,
                                        DriverSchema,
                                        DriverResponse)
from scr.cache.redis_geo import RedisGeo
from logging_log import logger


class DriverService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.drive_repo = DriversRepository(db=self.db)
        self.geo_redis = RedisGeo()

    async def create_driver(self,
                            create_driver: DriverCreate
                            ) -> DriverSchema:
        new_drive = await self.drive_repo.create_driver(
            driver_name=create_driver.name,
            driver_car=create_driver.car)
        await self.db.commit()
        logger.info(f'Новый водитель {new_drive} создан')
        return DriverSchema.model_validate(new_drive)

    async def update_status(self,
                            driver_id: int,
                            status: str,
                            lat: float | None = None,
                            lon: float | None = None
                            ) -> DriverResponseSchema:
        responce = await self.drive_repo.update_status_driver(
            driver_id,
            status,
            lat=lat,
            lon=lon
            )

        if not responce:
            raise SearchError()

        if status == 'online':
            if lat is not None and lon is not None:
                await self.geo_redis.add_geo_driver(
                    driver_id=driver_id,
                    lat=lat,
                    lon=lon
                    )
            else:
                pass
        else:
            await self.geo_redis.remove_driver(driver_id)
        await self.db.commit()
        return DriverResponseSchema.model_validate(responce)

    async def update_local(self,
                           driver_id: int,
                           lat: float,
                           lon: float):
        result = await self.drive_repo.update_location_driver(
            driver_id=driver_id,
            lat=lat,
            lon=lon
        )
        await self.geo_redis.add_geo_driver(
                        driver_id=driver_id,
                        lat=lat,
                        lon=lon
                        )
        await self.db.commit()
        return DriverResponseSchema.model_validate(result)

    async def search_driver(self, lat: float, lon: float):
        drivers = await self.geo_redis.get_geo_search(lat=lat, lon=lon)
        logger.info(f"Найдено {len(drivers)} водителей в радиусе {3} км")
        return drivers

    async def get_driver_id(
            self,
            driver_id: int
            ) -> DriverResponse:
        driver = await self.drive_repo.get_by_id(
            driver_id=driver_id
        )
        return DriverResponse.model_validate(driver)
