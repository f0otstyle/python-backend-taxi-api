from pydantic import BaseModel, ConfigDict, Field


class UserRegisterSchema(BaseModel):
    username: str
    password: str


class UserResponseSchema(BaseModel):
    id: int
    username: str = Field(validation_alias="name")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True)
