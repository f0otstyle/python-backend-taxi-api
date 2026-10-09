from datetime import datetime, timezone
import asyncio
from typing import cast
from uuid import uuid4

from fastapi import HTTPException

from error_handler import OrderError, SearchError
from scr.repositories.driver_repositories import DriversRepository
from scr.repositories.offer_repositories import OfferRepository
from scr.repositories.order_repositories import OrderTaxiRepository
from scr.repositories.payment_repositories import PaymentRepository
from scr.schemas.order_schemas import OrderCreate, OrderResponceSchema
from logging_log import logger
from sqlalchemy.ext.asyncio import AsyncSession
from scr.cache.redis import ORDER_ENTITY, RedisCachedBackend
from scr.cache.redis_geo import RedisGeo
from logging_log import log
from scr.websocket.manager import ConnectionManager

TIME = 5


class OrderTaxiService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_taxi_repo = OrderTaxiRepository(db=self.db)
        self.payment_repo = PaymentRepository(db=self.db)
        self.driver_repo = DriversRepository(db=self.db)
        self.redis_cached = RedisCachedBackend(cache_ttl_seconds=3600)
        self.redis_geo = RedisGeo()
        self.offer_repo = OfferRepository(db=db)
        self.manager = ConnectionManager()

    async def create_order_taxi(self,
                                user_id: int,
                                idempotency_key: str | None,
                                order_taxi_create: OrderCreate
                                ) -> OrderResponceSchema:
        existing = await self.order_taxi_repo.get_idempotency_key(
                idempotency_key
                )
        if existing:
            if existing.user_id != user_id:
                raise HTTPException(409, "Ключ уже занят другим запросом")
            logger.info(f"Повторный запрос с ключом {idempotency_key}")
            return OrderResponceSchema.model_validate(existing)

        lock_key = f"lock:order:{user_id}:{idempotency_key}"
        lock_token = str(uuid4())
        lock_acquired = await self.redis_cached.redis.set(
            lock_key,
            lock_token,
            nx=True,
            ex=30
            )

        if not lock_acquired:
            for _ in range(20):
                await asyncio.sleep(0.1)
                existing = await self.order_taxi_repo.get_idempotency_key(
                                idempotency_key
                                )
                if existing:
                    if existing.user_id != user_id:
                        raise HTTPException(409,
                                            "Ключ уже занят другим запросом"
                                            )
                    logger.info(f"Повторный запрос с ключом {idempotency_key}")
                    return OrderResponceSchema.model_validate(existing)
            raise HTTPException(409,
                                "Заказ ещё обрабатывается, повторите позже"
                                )
        try:
            user_card = await self.payment_repo.get_by_user_id(user_id)
            if not user_card or user_card.balance < order_taxi_create.price:
                logger.warning(
                    f'У пользователя {user_id} недостаточно средств'
                    )
                raise OrderError()

            driver_ids = await self.redis_geo.get_geo_search(
                lat=order_taxi_create.pickup_lat,
                lon=order_taxi_create.pickup_lon,
                radius=3.0
                )

            if not driver_ids:
                logger.warning('Нет свободных водителей')
                raise OrderError()

            best_driver = None

            for driver_id in driver_ids:
                driver = await self.driver_repo.get_by_id(driver_id)
                if not driver:
                    continue
                claimed = await self.driver_repo.claim_driver(driver_id)
                if claimed:
                    best_driver = driver
                    break
            if not best_driver:
                raise OrderError()

            new_order_taxi = await self.order_taxi_repo.create_order(
                user_id=user_id,
                idempotency_key=idempotency_key,
                driver_id=None,
                from_address=order_taxi_create.from_address,
                to_address=order_taxi_create.to_address,
                price=order_taxi_create.price,
                pickup_lat=order_taxi_create.pickup_lat,
                pickup_lon=order_taxi_create.pickup_lon,
                destination_lat=order_taxi_create.destination_lat,
                destination_lon=order_taxi_create.destination_lon
                )

            await self.offer_repo.create_accept_offer_cas(
                order_id=new_order_taxi.id,
                driver_ids=driver_ids
            )
            for driver_id in driver_ids:
                await self.manager.send_personal_message(
                    message={
                        "order_id": new_order_taxi.id,
                        "from_address": order_taxi_create.from_address,
                        "price": float(order_taxi_create.price)
                    },
                    driver_id=driver_id
                )

            await self.db.commit()
            await self.db.refresh(new_order_taxi)

            await self.redis_cached.delete(entity="order", identifier="list")

            logger.info(f'Новый заказ {new_order_taxi} такси создан')
            return OrderResponceSchema.model_validate(new_order_taxi)
        except Exception as e:
            await self.db.rollback()
            logger.error(f'Ошибка при создании заказа: {e}')
            raise e
        finally:
            unlock_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            await self.redis_cached.redis.eval(
                unlock_script,
                1,
                lock_key,
                lock_token
                )
            logger.info(f"Блокировка для {idempotency_key} снята")

    async def list_order(self) -> dict | list[dict]:
        cached_list_order = await self.redis_cached.get(
            entity=ORDER_ENTITY,
            identifier="list"
        )
        if cached_list_order:
            logger.info('Список заказов вывелся из кеша')
            await self.redis_cached.set(
                entity="order",
                identifier="list",
                value=[]
            )
            return cached_list_order

        rows = await self.order_taxi_repo.list_order()
        if not rows:
            logger.info('Список заказов пуст')

        orders = [OrderResponceSchema.model_validate(row) for row in rows]
        order_to_cache = [order.model_dump(mode='json') for order in orders]
        await self.redis_cached.set(
            entity="order",
            identifier="list",
            value=order_to_cache
        )

        return order_to_cache

    async def delete_id_orders(self, order_id) -> None:
        order = await self.order_taxi_repo.get_by_id(order_id)
        if not order:
            logger.error('Записи нету')
            raise SearchError()

        await self.offer_repo.delete_offers_by_order_id(order_id)
        await self.order_taxi_repo.delete_id_order(order_id)

        await self.redis_cached.delete(
            entity="order",
            identifier=str(order_id)
            )

        await self.redis_cached.delete(
                    entity=ORDER_ENTITY,
                    identifier="list"
                    )

        await self.db.commit()
        return None

    async def history_get(self) -> list[OrderResponceSchema]:
        rows = await self.order_taxi_repo.get_history()
        return [OrderResponceSchema.model_validate(row) for row in rows]

    # @log
    async def get_order_id(self, order_id) -> dict | list[dict]:
        cached_order = await self.redis_cached.get(
            entity=ORDER_ENTITY,
            identifier=str(order_id)
            )
        if cached_order:
            logger.info(f"Заказ {order_id} взят из кэша!")
            return cached_order

        lock_key = f"lock:taxi:order:{order_id}"
        lock_acquired = await self.redis_cached.redis.set(
            lock_key,
            "1",
            nx=True,
            ex=10
            )
        if lock_acquired:
            logger.warning(
                f'DB HIT (С ЗАЩИТОЙ): Только я иду в БД для заказа {order_id}'
            )
            try:
                row = await self.order_taxi_repo.get_by_id(order_id)
                if row:
                    order = OrderResponceSchema.model_validate(row)
                    order_to_cache = order.model_dump(mode='json')

                    await self.redis_cached.set(
                        entity="order",
                        identifier=str(order_id),
                        value=order_to_cache
                        )
                    logger.info(f'Кэш для заказа {order_id} обновлен')
                    return order_to_cache
            finally:
                await self.redis_cached.redis.delete(lock_key)

            logger.warning(f'Попытка найти несуществующий заказ {order_id}')
            raise SearchError()
        else:
            logger.info(
                f'CACHE WAIT: Жду, пока другой поток обновит кэш ({order_id})'
            )
            await asyncio.sleep(0.05)
            order_cache = await self.redis_cached.get(
                entity="order",
                identifier=str(order_id)
                )
            if order_cache:
                logger.info(
                    f'CACHE HIT: Заказ по {order_id} найден в кэше'
                    )
                return cast(dict, order_cache)

            raise SearchError()
