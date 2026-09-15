from sqlalchemy.ext.asyncio import AsyncSession
from scr.repositories.payment_repositories import PaymentRepository
from scr.schemas.payment_schemas import MoneySchema, PaymentResponceSchema


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_rep = PaymentRepository(db=self.db)

    async def top_up_balance(self,
                             user_id: int,
                             payment: MoneySchema
                             ) -> PaymentResponceSchema:
        updated_card = await self.payment_rep.upsert_balance(
            user_id=user_id,
            money=payment.money
            )
        await self.db.commit()
        return PaymentResponceSchema.model_validate(updated_card)
