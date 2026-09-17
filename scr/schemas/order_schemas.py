from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class OrderCreate(BaseModel):
    from_address: str
    to_address: str
    price: Decimal


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
