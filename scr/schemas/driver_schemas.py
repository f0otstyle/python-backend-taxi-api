from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from enum import Enum


class DriverStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class DriverCreate(BaseModel):
    name: str
    car: str


class DriverUpdate(BaseModel):
    name: str
    car: str
    status: DriverStatus | None = None
    lat: float | None = None
    lon: float | None = None


class DriverUpdateStatusSchema(BaseModel):
    status: DriverStatus | None = None
    lat: float | None = None
    lon: float | None = None


class DriverUpdateLocationSchema(BaseModel):
    lat: float | None = None
    lon: float | None = None


class DriverSchema(BaseModel):
    id: int
    name: str
    car: str
    money: Decimal
    status: DriverStatus
    rating: float
    model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True)


class DriverResponseSchema(BaseModel):
    id: int
    name: str
    car: str
    money: Decimal
    status: DriverStatus
    rating: float
    lat: float | None = None
    lon: float | None = None
    model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True)


class DriverResponse(BaseModel):
    id: int
    name: str
    car: str
    status: DriverStatus
    rating: float
    money: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )
