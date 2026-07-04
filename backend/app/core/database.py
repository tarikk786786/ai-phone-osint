"""Database engine, session factories, and helpers.

Supports:
- PostgreSQL via SQLAlchemy (async)
- MongoDB via Motor (async)
- Redis via redis-py (async)
"""

from __future__ import annotations

from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# ── PostgreSQL ──────────────────────────────────────────

postgres_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    echo=settings.DEBUG,
)

PostgresSessionLocal = async_sessionmaker(
    postgres_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session (for FastAPI dependency injection)."""
    async with PostgresSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ── MongoDB ─────────────────────────────────────────────

_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
    return _mongo_client


def get_mongo_db() -> AsyncIOMotorDatabase:
    client = get_mongo_client()
    return client.get_default_database()


async def close_mongo() -> None:
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None


# ── Redis ───────────────────────────────────────────────

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


# ── Lifecycle hooks ─────────────────────────────────────

async def init_db() -> None:
    """Run on startup — create tables, warm connections."""
    from app.models.base import Base  # noqa: F401
    from app.models.user import User  # noqa: F401
    from app.models.phone import PhoneLookup  # noqa: F401
    from app.models.api_key import ApiKey  # noqa: F401
    from app.models.audit_log import AuditLog  # noqa: F401

    async with postgres_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Warm connections
    _ = get_redis()
    _ = get_mongo_client()


async def close_db() -> None:
    await postgres_engine.dispose()
    await close_mongo()
    await close_redis()
