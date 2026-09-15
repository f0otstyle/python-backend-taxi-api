from ..core.config import settings
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    AsyncSession,
                                    async_sessionmaker)
from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
from authx import AuthXConfig
from datetime import timedelta

engine = create_async_engine(
    settings.DATABASE_URL_asyncpg,
    echo=True,
)
AsyncSessionLocal = async_sessionmaker(engine,
                                       class_=AsyncSession,
                                       expire_on_commit=False)


config = AuthXConfig(
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'SECRET-KEY'),
    JWT_TOKEN_LOCATION=['cookies'],
    JWT_ACCESS_COOKIE_NAME='my_cookie',
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=1),
    JWT_COOKIE_CSRF_PROTECT=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = engine
    yield
    await engine.dispose()


async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
