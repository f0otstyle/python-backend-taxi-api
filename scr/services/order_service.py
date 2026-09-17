from datetime import datetime, timezone


from error_handler import OrderError, SearchError
from scr.repositories.driver_repositories import DriversRepository
from scr.repositories.order_repositories import OrderTaxiRepository
from scr.repositories.payment_repositories import PaymentRepository
from scr.schemas.order_schemas import OrderCreate, OrderResponceSchema
from logging_log import logger
from sqlalchemy.ext.asyncio import AsyncSession


TIME = 5


class OrderTaxiService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_taxi_repo = OrderTaxiRepository(db=self.db)
        self.payment_repo = PaymentRepository(db=self.db)
        self.driver_repo = DriversRepository(db=self.db)

    async def create_order_taxi(self,
                                user_id: int,
                                idempotency_key: str | None,
                                order_taxi_create: OrderCreate
                                ) -> OrderResponceSchema:
        existing = await self.order_taxi_repo.get_idempotency_key(
                idempotency_key
                )
        if existing:
            logger.info(f"Повторный запрос с ключом {idempotency_key}")
            return OrderResponceSchema.model_validate(existing)

        current_time = datetime.now(timezone.utc).timestamp()
        duplicate = await self.order_taxi_repo.get_duplicate(
            user_id=user_id,
            to_address=order_taxi_create.to_address
            )

        if duplicate:
            created_at = duplicate.created_at.timestamp()
            time_diff = current_time - created_at
            if time_diff < TIME:
                logger.warning(
                    f'Попытка создать дубликат заказа для {
                        order_taxi_create.to_address
                        } (прошло {time_diff:.1f} с)'
                    )
                raise OrderError()
            logger.info('Можно сделать новый заказ')
        try:
            user_card = await self.payment_repo.get_by_user_id(user_id)
            if not user_card or user_card.balance < order_taxi_create.price:
                logger.warning(
                    f'У пользователя {user_id} недостаточно средств'
                    )
                raise OrderError()

            driver = await self.driver_repo.get_driver()

            if not driver:
                logger.warning('Нет свободных водителей')
                raise OrderError()

            user_card.balance -= order_taxi_create.price
            driver.money += order_taxi_create.price

            self.db.add(user_card)
            self.db.add(driver)

            new_order_taxi = await self.order_taxi_repo.create_order_taxi(
                user_id=user_id,
                idempotency_key=idempotency_key,
                driver_id=driver.id,
                from_address=order_taxi_create.from_address,
                to_address=order_taxi_create.to_address,
                price=order_taxi_create.price)

            await self.db.commit()
            await self.db.refresh(new_order_taxi)

            logger.info(f'Новый заказ {new_order_taxi} такси создан')
            return OrderResponceSchema.model_validate(new_order_taxi)
        except Exception as e:
            await self.db.rollback()
            logger.error(f'Ошибка при создании заказа: {e}')
            raise e

    async def list_order(self) -> list[OrderResponceSchema]:
        rows = await self.order_taxi_repo.list_order()
        if not rows:
            logger.info('Список заказов пуст')
        return [OrderResponceSchema.model_validate(row) for row in rows]

    async def delete_id_orders(self, order_id) -> None:
        order = await self.order_taxi_repo.get_by_id(order_id)
        if not order:
            logger.error('Записи нету')
            raise SearchError()

        await self.order_taxi_repo.delete_id_order(order_id)
        await self.db.commit()
        return None

    async def history_get(self) -> list[OrderResponceSchema]:
        rows = await self.order_taxi_repo.get_history()
        return [OrderResponceSchema.model_validate(row) for row in rows]

    async def get_order_id(self, order_id) -> OrderResponceSchema:
        row = await self.order_taxi_repo.get_by_id(order_id)
        if not row:
            raise SearchError()

        return OrderResponceSchema.model_validate(row)
