from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from scr.models.payment_models import PaymentORM
from logging_log import logger


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id):
        return await self.db.get(PaymentORM, user_id)

    async def upsert_balance(self, user_id: int,
                             money: Decimal
                             ):
        card = await self.get_by_user_id(user_id)
        if card:
            card.balance += money
        else:
            card = PaymentORM(user_id=user_id, balance=money)
            self.db.add(card)

        await self.db.flush()
        await self.db.refresh(card)
        logger.info(f'Баланс пользователя {user_id} пополнен на {money} руб')
        return card
