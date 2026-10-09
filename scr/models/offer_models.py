from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, func

from scr.schemas.offer_schemas import OfferStatus

from .base import Base
from sqlalchemy.orm import mapped_column, Mapped


class OfferRideORM(Base):
    __tablename__ = "offer_ride_order"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("order_taxi.id"),
        nullable=False
        )
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id"),
        nullable=False
        )
    status: Mapped[str] = mapped_column(
        String(20),
        default=OfferStatus.PENDING.value
        )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
