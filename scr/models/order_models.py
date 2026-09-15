from datetime import datetime
from sqlalchemy import TIMESTAMP, ForeignKey, Numeric, func

from .base import Base, str_256, money_money
from sqlalchemy.orm import mapped_column, Mapped


class OrderTaxiORM(Base):
    __tablename__ = "order_taxi"

    id: Mapped[int] = mapped_column(primary_key=True)
    idempotency_key: Mapped[str_256] = mapped_column(nullable=False,
                                                     unique=True)
    from_address: Mapped[str_256]
    to_address: Mapped[str_256] = mapped_column(nullable=False)
    price: Mapped[money_money] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                                 server_default=func.now())
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"),
                                           nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
                                         nullable=False)
