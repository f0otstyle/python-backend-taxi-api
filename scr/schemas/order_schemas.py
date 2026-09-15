from decimal import Decimal
from pydantic import BaseModel


class OrderCreate(BaseModel):
    from_address: str
    to_address: str
    price: Decimal


class OrderResponceSchema(BaseModel):
    from_address: str
    to_address: str
    price: Decimal
