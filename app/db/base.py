from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from typing import AsyncGenerator

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Async engine and session
async_engine = None
AsyncSessionLocal = None

# Sync engine and session for Alembic
sync_engine = None
SessionLocal = None


def get_database_url(sync: bool = False) -> str:
    """Get the database URL from the environment."""
    url = settings.DATABASE_URL
    if sync:
        # Convert async URL to sync URL by replacing asyncpg with psycopg2
        return url.replace("asyncpg", "psycopg2")
    return url


def get_sync_database_url() -> str:
    """Get the synchronous database URL."""
    return get_database_url(sync=True)


def get_async_database_url() -> str:
    """Get the asynchronous database URL."""
    return get_database_url(sync=False)


async def init_db():
    """Initialize the async database connection."""
    global async_engine
    global AsyncSessionLocal
    if async_engine is None:
        async_engine = create_async_engine(
            get_async_database_url(),
            echo=False,
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return async_engine


def init_sync_db():
    """Initialize the sync database connection."""
    global sync_engine
    global SessionLocal
    if sync_engine is None:
        sync_engine = create_engine(
            get_sync_database_url(),
            echo=False,
        )
        SessionLocal = sessionmaker(
            bind=sync_engine,
            expire_on_commit=False,
            autoflush=False,
        )
    return sync_engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    if AsyncSessionLocal is None:
        await init_db()
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db():
    """Get a sync database session."""
    if SessionLocal is None:
        init_sync_db()
    with SessionLocal() as session:
        yield session
