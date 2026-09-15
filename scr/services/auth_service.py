import bcrypt
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from logging_log import logger
from scr.schemas.auth_schemas import UserRegisterSchema, UserResponseSchema
from scr.repositories.auth_repositories import AuthRepository


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_repositories = AuthRepository(db=self.db)

    async def create_users(self,
                           user: UserRegisterSchema
                           ) -> UserResponseSchema:
        existing = await self.auth_repositories.get_by_username(user.username)
        if existing:
            raise HTTPException(
                status_code=400,
                detail='Пользователь уже существует'
            )
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(
            user.password.encode('utf-8'),
            salt
        ).decode('utf-8')
        new_user = await self.auth_repositories.create_users(
            username=user.username,
            hashed_password=hashed_password
            )
        await self.db.commit()
        logger.info(f'Новый пользователь {new_user} создан')
        return UserResponseSchema.model_validate(new_user)

    async def get_user_by_username(self, username: str):
        return await self.auth_repositories.get_by_username(username)
