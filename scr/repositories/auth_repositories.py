from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from scr.models.auth_models import AuthORM
from logging_log import logger


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str):
        existing = await self.db.scalar(
                select(AuthORM).where(AuthORM.name == username)
                )

        return existing

    async def create_users(self, username: str, hashed_password: str):
        new_user = AuthORM(name=username, password=hashed_password)
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        logger.info(f'Пользователь создан {new_user}')
        return new_user
