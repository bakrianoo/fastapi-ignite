"""
Application startup and shutdown events
"""
import logging
from typing import Callable

from src.cache.backends.factory import init_cache_backend, close_cache_backend
from src.core.config import settings
from src.db.session import create_db_engine, dispose_db_engine
from src.schedulers.scheduler import init_scheduler, shutdown_scheduler


logger = logging.getLogger(__name__)


def create_start_app_handler() -> Callable:
    """
    Factory for creating the startup event handler
    """
    async def start_app() -> None:
        """
        Initialize services on application startup
        """
        logger.info("Executing application startup handler")
          # Initialize database
        await create_db_engine()
        logger.info("Database connection established")
        
        # Initialize the cache backend
        await init_cache_backend()
        logger.info(f"Cache backend initialized (type: {settings.CACHE_BACKEND_TYPE})")
          # Initialize scheduler if enabled in config and not in test mode
        if settings.ENV != "test" and settings.SCHEDULER_ENABLED:
            await init_scheduler()
            logger.info("Task scheduler initialized")
        elif settings.ENV != "test" and not settings.SCHEDULER_ENABLED:
            logger.info("Task scheduler disabled in configuration")
        
    return start_app


def create_stop_app_handler() -> Callable:
    """
    Factory for creating the shutdown event handler
    """
    async def stop_app() -> None:
        """
        Cleanup services on application shutdown
        """
        logger.info("Executing application shutdown handler")        # Shutdown scheduler if it was started
        if settings.ENV != "test" and settings.SCHEDULER_ENABLED:
            await shutdown_scheduler()
            logger.info("Task scheduler shutdown")
        
        # Close the cache backend
        await close_cache_backend()
        logger.info("Cache backend closed")
        
        # Dispose database connections
        await dispose_db_engine()
        logger.info("Database connections disposed")
        
    return stop_app
