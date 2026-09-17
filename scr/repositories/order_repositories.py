from decimal import Decimal

from sqlalchemy import and_, select

from sqlalchemy.ext.asyncio import AsyncSession
from scr.models.order_models import OrderTaxiORM
from logging_log import logger


class OrderTaxiRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(OrderTaxiORM))
        return result.scalars().all()

    async def get_by_id(self, order_id):
        return await self.db.get(OrderTaxiORM, order_id)

    async def create_order_taxi(self, user_id: int,
                                idempotency_key: str | None,
                                from_address: str,
                                to_address: str,
                                price: Decimal,
                                driver_id: int | None = None
                                ):
        new_order_taxi = OrderTaxiORM(user_id=user_id,
                                      from_address=from_address,
                                      idempotency_key=idempotency_key,
                                      to_address=to_address,
                                      price=price,
                                      driver_id=driver_id
                                      )
        self.db.add(new_order_taxi)
        await self.db.flush()
        await self.db.refresh(new_order_taxi)
        logger.info(f'Заказ {
            new_order_taxi
            } создан для пользователя {
                user_id
                }, машина приедет по адресу {
                    from_address
                    } и должна доехать до адреса {
                        to_address
                        } стоимость поездки {
                            price
                            } руб')
        return new_order_taxi

    async def list_order(self):
        result = await self.db.execute(select(OrderTaxiORM))
        return result.scalars().all()

    async def delete_id_order(self, order_id):
        order = await self.get_by_id(order_id)
        if order:
            await self.db.delete(order)
            await self.db.flush()
            return True
        return False

    async def history_order_taxi(self):
        result = await self.db.execute(
            select(OrderTaxiORM)
            .order_by(OrderTaxiORM.created_at.desc())
            )
        return result.scalars().all()

    async def get_idempotency_key(self, idempotency_key):
        result = await self.db.execute(
            select(OrderTaxiORM)
            .where(OrderTaxiORM.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def get_duplicate(self, to_address: str, user_id: int):
        return await self.db.scalar(select(OrderTaxiORM).where(
                and_(
                    OrderTaxiORM.to_address == to_address,
                    OrderTaxiORM.user_id == user_id
                )
            ).order_by(OrderTaxiORM.created_at.desc()))

    async def get_history(self):
        result = await self.db.execute(
            select(OrderTaxiORM)
            .order_by(OrderTaxiORM.created_at.desc())
            )
        return result.scalars().all()
