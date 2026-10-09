from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from scr.repositories.offer_repositories import OfferRepository
from scr.repositories.order_repositories import OrderTaxiRepository
from scr.schemas.offer_schemas import OfferResponceSchemas
from scr.schemas.order_schemas import OrderResponceSchema


class OfferService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.offer_repo = OfferRepository(db=db)
        self.order_repo = OrderTaxiRepository(db=db)

    async def accept_offer(self, offer_id: int):
        offer = await self.offer_repo.accept_offer_cas(offer_id)
        if not offer:
            raise HTTPException(
                status_code=409,
                detail="Этот заказ уже принял другой водитель или время оффера истекло"
            )
        updated_order = await self.order_repo.update_order_status(
            order_id=offer.order_id,
            new_status="accepted",
            expected_status='created',
            expected_driver_id=offer.driver_id
            )
        if not updated_order:
            raise HTTPException(
                status_code=409,
                detail="Не удалось закрепить заказ. Возможно, он был отменен."
            )

        await self.db.commit()
        return OrderResponceSchema.model_validate(updated_order)

    async def get_offers(self, order_id: int):
        offers = await self.offer_repo.get_offers_by_order_id(order_id)
        return [OfferResponceSchemas.model_validate(offer) for offer in offers]
