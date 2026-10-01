from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class OrderCreate(BaseModel):
    from_address: str
    to_address: str
    price: Decimal
    pickup_lat: float
    pickup_lon: float
    destination_lat: float | None = None
    destination_lon: float | None = None


class OrderResponceSchema(BaseModel):
    id: int
    from_address: str
    to_address: str
    price: Decimal
    driver_id: int | None
    created_at: datetime
    user_id: int
    model_config = ConfigDict(
                from_attributes=True,
                populate_by_name=True)
