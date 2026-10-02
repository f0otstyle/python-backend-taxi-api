from fastapi import HTTPException
from scr.cache.redis_geo import RedisGeo
from scr.repositories.driver_repositories import DriversRepository
from scr.repositories.order_repositories import OrderTaxiRepository
from logging_log import logger
from sqlalchemy.ext.asyncio import AsyncSession

from scr.schemas.driver_schemas import DriverStatus
from scr.schemas.order_schemas import OrderStatus


class RideService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderTaxiRepository(db)
        self.driver_repo = DriversRepository(db)
        self.geo = RedisGeo()

    async def start_trip(self, order_id: int, user_id: int):
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            logger.info(f'Заказ {order_id} не найден')
            raise HTTPException(status_code=404, detail="Заказ не найден")
        if order.user_id != user_id:
            raise HTTPException(403, "Это не ваш заказ")
        updated = await self.order_repo.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.IN_PROGRESS.value,
            expected_status=OrderStatus.CREATED.value,
            expected_driver_id=order.driver_id)
        if not updated:
            raise HTTPException(409, "Поездка уже начата или заказ неактивен")
        await self.db.commit()
        return updated

    async def finish_ride(self,
                          order_id: int,
                          user_id: int
                          ):
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            logger.info(f'Заказ {order_id} не найден')
            raise HTTPException(status_code=404, detail="Заказ не найден")
        if order.user_id != user_id:
            raise HTTPException(403, "Это не ваш заказ")
        updated = await self.order_repo.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.COMPLETED.value,
            expected_status=OrderStatus.IN_PROGRESS.value,
            expected_driver_id=order.driver_id
        )
        if not updated:
            raise HTTPException(
                409,
                "Поездка уже закончилась или заказ неактивен"
                )
        if order.driver_id:
            driver = await self.driver_repo.get_by_id(order.driver_id)
            await self.driver_repo.set_driver_status(order.driver_id,
                                                     DriverStatus.ONLINE.value)
            if driver and driver.lat is not None and driver.lon is not None:
                await self.geo.add_geo_driver(
                    driver.id,
                    driver.lat,
                    driver.lon
                    )
        await self.db.commit()
        return updated
