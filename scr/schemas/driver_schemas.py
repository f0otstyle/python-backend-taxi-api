from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DriverCreate(BaseModel):
    name: str
    car: str


class DriverResponseSchema(BaseModel):
    id: int
    name: str
    car: str
    money: Decimal
    model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True)
