from .base import Base, str_256, money_money
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Numeric, Enum
from scr.schemas.driver_schemas import DriverStatus


class DriversORM(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_256] = mapped_column(nullable=False)
    car: Mapped[str_256] = mapped_column(nullable=False)
    money: Mapped[money_money] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[DriverStatus] = mapped_column(
        Enum(DriverStatus, native_enum=False,
            values_callable=lambda e: [m.value for m in e]),
        default=DriverStatus.OFFLINE,
        server_default="offline"
        )
    lat: Mapped[float | None] = mapped_column(nullable=True, default=None)
    lon: Mapped[float | None] = mapped_column(nullable=True, default=None)
    rating: Mapped[float] = mapped_column(nullable=False, default=5.0)
