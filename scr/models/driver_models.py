from .base import Base, str_256, money_money
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Numeric


class DriversORM(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_256] = mapped_column(nullable=False)
    car: Mapped[str_256] = mapped_column(nullable=False)
    money: Mapped[money_money] = mapped_column(Numeric(10, 2), default=0)
