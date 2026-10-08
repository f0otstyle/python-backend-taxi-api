from decimal import Decimal

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from scr.models.payment_models import PaymentORM
from logging_log import logger


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id):
        result = await self.db.execute(
            select(PaymentORM).where(PaymentORM.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_balance(self, user_id: int,
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

    async def update_payment_user(self, user_id: int, payment: Decimal):
        user_payment = (update(PaymentORM)
                        .values(balance=PaymentORM.balance - payment)
                        .where(
                            and_(
                                PaymentORM.user_id == user_id,
                                PaymentORM.balance >= payment
                                )
                            ).returning(PaymentORM))
        result = await self.db.execute(user_payment)
        return result.scalar_one_or_none()

    async def get_balance_users(self, user_id):
        user_balance = (select(PaymentORM)
                        .where(PaymentORM.user_id == user_id)
                        )
        result = await self.db.execute(user_balance)
        return result.scalar_one_or_none()
