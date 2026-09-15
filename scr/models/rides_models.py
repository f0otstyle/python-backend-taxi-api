from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, func

from .base import Base
from sqlalchemy.orm import mapped_column, Mapped


class RidesORM(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order_taxi.id",
                                                     ondelete="CASCADE"),
                                                     nullable=False)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"),
                                           nullable=True)
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True)
    duration: Mapped[int] = mapped_column(nullable=True)
