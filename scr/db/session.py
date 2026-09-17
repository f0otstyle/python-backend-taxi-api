from scr.models.base import Base

from ..core.config import settings
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    AsyncSession,
                                    async_sessionmaker)
from contextlib import asynccontextmanager
from fastapi import FastAPI

engine = create_async_engine(
    settings.DATABASE_URL_asyncpg,
    echo=True,
)
AsyncSessionLocal = async_sessionmaker(engine,
                                       class_=AsyncSession,
                                       expire_on_commit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
