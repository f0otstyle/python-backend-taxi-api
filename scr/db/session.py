from scr.cache.redis import Ratelimit, RedisCachedBackend
from scr.models.base import Base

from ..core.config import settings
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    AsyncSession,
                                    async_sessionmaker)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

engine = create_async_engine(
    settings.DATABASE_URL_asyncpg,
    echo=True,
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.redis_cache = RedisCachedBackend(cache_ttl_seconds=3600)
    app.state.redis_rate_limiter = Ratelimit()

    yield

    await engine.dispose()


async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_cache(request: Request) -> RedisCachedBackend:
    return request.app.state.redis_cache


async def get_rate_limiter(request: Request) -> Ratelimit:
    return request.app.state.redis_rate_limiter
