from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from scr.models.driver_models import DriversORM
from logging_log import logger


class DriversRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

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
