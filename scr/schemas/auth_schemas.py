from pydantic import BaseModel


class UserRegisterSchema(BaseModel):
    username: str
    password: str


class UserResponseSchema(BaseModel):
    id: int
    username: str
