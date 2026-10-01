from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from scr.models.driver_models import DriversORM
from logging_log import logger
from scr.schemas.driver_schemas import DriverStatus


class DriversRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, driver_id: int):
        result = await self.db.execute(select(DriversORM).where(
            and_(
                DriversORM.id == driver_id,
                DriversORM.status == 'online'
            )
        ))
        return result.scalar_one_or_none()

    async def create_driver(self, driver_name: str, driver_car: str):
        new_driver = DriversORM(name=driver_name, car=driver_car)
        logger.info(
            f'Водитель {
                driver_name
                } создан и будет ездить на автомобили {
                driver_car
                }'
            )
        self.db.add(new_driver)
        await self.db.flush()
        await self.db.refresh(new_driver)
        return new_driver

    async def get_driver(self):
        stmt = (select(DriversORM)
                .order_by(func.random())
                .limit(1)
                .with_for_update(skip_locked=True)
                )
        return await self.db.scalar(stmt)

    async def update_status_driver(self,
                                   driver_id: int,
                                   status: str,
                                   lat: float,
                                   lon: float
                                   ):
        stmt = (update(DriversORM)
                .where(DriversORM.id == driver_id)
                .values(status=status, lat=lat, lon=lon)
                .returning(DriversORM)
                )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_location_driver(self,
                                     driver_id: int,
                                     lat: float,
                                     lon: float
                                     ):
        stmt = (
            update(DriversORM)
            .where(DriversORM.id == driver_id)
            .values(lat=lat, lon=lon)
            .returning(DriversORM)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def claim_driver(self, driver_id: int):
        stmt = (update(DriversORM)
                .where(DriversORM.id == driver_id,
                       DriversORM.status == DriverStatus.ONLINE)
                .values(status=DriverStatus.BUSY)
                .returning(DriversORM))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
