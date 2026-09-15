from pydantic import BaseModel
from decimal import Decimal


class MoneySchema(BaseModel):
    money: Decimal


class PaymentResponceSchema(BaseModel):
    money: Decimal
