from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal


class MoneySchema(BaseModel):
    money: Decimal


class PaymentResponceSchema(BaseModel):
    id: int
    user_id: int
    money: Decimal = Field(alias="balance")
    model_config = ConfigDict(
                from_attributes=True,
                populate_by_name=True)
