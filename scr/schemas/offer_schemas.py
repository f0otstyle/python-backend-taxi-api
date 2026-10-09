from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class OfferStatus(str, Enum):
    PENDING = "pending"      # Ожидает решения водителя
    ACCEPTED = "accepted"    # Водитель принял заказ
    REJECTED = "rejected"    # Водитель отклонил
    EXPIRED = "expired"      # Истекло время ожидания


class OfferSchemas(BaseModel):
    id: int
    order_id: int
    driver_id: int
    status: OfferStatus
    created_at: datetime


class OfferResponceSchemas(BaseModel):
    id: int
    order_id: int
    driver_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
