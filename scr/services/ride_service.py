from fastapi import HTTPException
from scr.cache.redis_geo import RedisGeo
from scr.cache.redis import ORDER_ENTITY, RedisCachedBackend
from scr.repositories.driver_repositories import DriversRepository
from scr.repositories.order_repositories import OrderTaxiRepository
from logging_log import logger
from sqlalchemy.ext.asyncio import AsyncSession
from scr.repositories.payment_repositories import PaymentRepository
from scr.schemas.driver_schemas import DriverStatus
from scr.schemas.order_schemas import OrderStatus


class RideService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderTaxiRepository(db)
        self.driver_repo = DriversRepository(db)
        self.payment_repo = PaymentRepository(db)
        self.geo = RedisGeo()
        self.cache = RedisCachedBackend(cache_ttl_seconds=3600)

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
        await self.cache.delete(entity=ORDER_ENTITY, identifier=str(order_id))
        await self.cache.delete(entity=ORDER_ENTITY, identifier="list")
        return updated

    async def finish_payment_for_the_trip(
            self,
            order_id: int
            ):
        order_taxi_payment = await self.order_repo.get_by_id(order_id)
        if not order_taxi_payment:
            logger.info(f'Заказа {order_id} не существует')
            raise HTTPException(
                409,
                "Поездка уже закончилась или заказ неактивен"
            )

        payment_taxi_driver = await self.driver_repo.update_payment_driver(
            driver_id=order_taxi_payment.driver_id,
            payment=order_taxi_payment.price
            )

        if not payment_taxi_driver:
            await self.db.rollback()
            logger.info(f'Оплата водителю {order_taxi_payment.driver_id} не начислена')
            raise HTTPException(
                    500,
                    "Оплата не прошла"
                )

        payment_taxi_user = await self.payment_repo.update_payment_user(
                user_id=order_taxi_payment.user_id,
                payment=order_taxi_payment.price
                )

        if not payment_taxi_user:
            await self.db.rollback()
            logger.info(f'Списание денег пользователя {order_taxi_payment.user_id} не прошла')
            raise HTTPException(
                409,
                "Оплата не прошла"
            )
        return payment_taxi_user

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

        await self.finish_payment_for_the_trip(
            order_id=order_id
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
        await self.cache.delete(entity=ORDER_ENTITY, identifier=str(order_id))
        await self.cache.delete(entity=ORDER_ENTITY, identifier="list")
        return updated
