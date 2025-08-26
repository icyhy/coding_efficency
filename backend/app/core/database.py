from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Convert SQLite URL to async format
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite://"):
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")

# Create async engine
engine = create_async_engine(
    database_url,
    echo=True,  # Set to False in production
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.models import user, repository, commit, merge_request, analytics_cache
        await conn.run_sync(Base.metadata.create_all)