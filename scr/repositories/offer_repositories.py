from sqlalchemy import and_, insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from scr.models.offer_models import OfferRideORM
from scr.schemas.offer_schemas import OfferStatus


class OfferRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_accept_offer_cas(
        self,
        order_id: int,
        driver_ids: list[int]
         ):
        if not driver_ids:
            return []

        stmt = (insert(OfferRideORM)
                .values([
                    {
                        "order_id": order_id,
                        "driver_id": driver_id,
                        "status": OfferStatus.PENDING.value
                        } for driver_id in driver_ids
                    ]).returning(OfferRideORM))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def accept_offer_cas(
            self,
            offer_id: int
            ) -> OfferRideORM | None:
        stmt = (update(OfferRideORM)
                .where(
                    and_(OfferRideORM.id == offer_id,
                         OfferRideORM.status == OfferStatus.PENDING.value)
                    )
                .values(status=OfferStatus.ACCEPTED.value)
                .returning(OfferRideORM)
                )
        offer_order = await self.db.execute(stmt)
        return offer_order.scalar_one_or_none()

    async def get_offers_by_order_id(self, order_id: int):
        stmt = (select(OfferRideORM).where(OfferRideORM.order_id == order_id))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_offers_by_order_id(self, order_id: int) -> int:
        stmt = delete(OfferRideORM).where(OfferRideORM.order_id == order_id)
        result = await self.db.execute(stmt)
        return result.rowcount
