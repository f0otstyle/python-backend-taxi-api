from decimal import Decimal

from sqlalchemy.orm import DeclarativeBase
from typing import Annotated
from sqlalchemy import Numeric, String


str_256 = Annotated[str, String(256)]
money_money = Annotated[Decimal, Numeric(10, 2)]


class Base(DeclarativeBase):
    pass
