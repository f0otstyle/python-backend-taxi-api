from .base import Base, str_256
from sqlalchemy.orm import mapped_column, Mapped


class AuthORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_256] = mapped_column(nullable=False)
    password: Mapped[str_256] = mapped_column(nullable=False)
