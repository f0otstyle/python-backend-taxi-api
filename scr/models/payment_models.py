from sqlalchemy import ForeignKey

from .base import Base, money_money
from sqlalchemy.orm import mapped_column, Mapped


class PaymentORM(Base):
    __tablename__ = "taxi_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
                                         unique=True
                                         )
    balance: Mapped[money_money] = mapped_column(nullable=False,
                                                 default=0
                                                 )
