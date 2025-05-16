"""
Database session management
"""
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
)

from src.core.config import settings
from src.db.base import Base


logger = logging.getLogger(__name__)

# Global engine instance
engine: AsyncEngine = None
async_session_factory: async_sessionmaker = None


async def create_db_engine() -> None:
    """
    Initialize the database engine
    """
    global engine, async_session_factory
    
    logger.info("Creating database engine")
    engine = create_async_engine(
        str(settings.DATABASE_URI),
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    
    async_session_factory = async_sessionmaker(
        engine, expire_on_commit=False, autoflush=False
    )


async def dispose_db_engine() -> None:
    """
    Close database connections
    """
    global engine
    
    if engine:
        logger.info("Closing database connections")
        await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session
    """
    if async_session_factory is None:
        await create_db_engine()
        
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def init_db() -> None:
    """
    Create database tables if they don't exist
    """
    global engine
    
    if engine is None:
        await create_db_engine()
    
    logger.info("Creating database tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
