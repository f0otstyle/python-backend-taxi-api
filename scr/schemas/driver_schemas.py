from pydantic import BaseModel


class DriverCreate(BaseModel):
    name: str
    car: str


class DriverResponseSchema(BaseModel):
    name: str
    car: str
