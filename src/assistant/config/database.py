from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator

from assistant.config.app import config

engine = None
AsyncSessionLocal = None

async def init_db():
    """Initialize the database connection."""
    global engine
    global AsyncSessionLocal
    if engine is None:
        engine = create_async_engine(
            get_database_url(),
            echo=config.get("database.log_print"),
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return engine

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    if AsyncSessionLocal is None:
        await init_db()
    async with AsyncSessionLocal() as session:
        yield session

def get_database_url(sync: bool = False) -> str:
    """Get the database URL from the environment."""
    testing = config.get("app.testing")
    if testing:
        url = config.get("database.test_url")
    else:
        url = config.get("database.url")
    if not url:
        raise (
            ValueError("TEST_DATABASE_URL_SYNC environment variable is not set")
            if testing
            else ValueError("DATABASE_URL_SYNC environment variable is not set")
        )
    return url
