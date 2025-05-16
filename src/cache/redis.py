"""
Redis connection management
"""
import logging
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from src.core.config import settings


logger = logging.getLogger(__name__)

# Global Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None


async def init_redis_pool() -> None:
    """
    Initialize Redis connection pool
    """
    global redis_pool
    
    logger.info("Initializing Redis connection pool")
    redis_pool = redis.ConnectionPool.from_url(
        url=str(settings.REDIS_URI),
        max_connections=10,
        decode_responses=True,  # Automatically decode responses to Python strings
    )


async def close_redis_pool() -> None:
    """
    Close Redis connection pool
    """
    global redis_pool
    
    if redis_pool:
        logger.info("Closing Redis connection pool")
        await redis_pool.disconnect()
        redis_pool = None


async def get_redis() -> Redis:
    """
    Get Redis client from pool
    
    Can be used as a FastAPI dependency
    """
    global redis_pool
    
    if redis_pool is None:
        await init_redis_pool()
    
    async with redis.Redis(connection_pool=redis_pool) as conn:
        yield conn
