"""
Redis cache backend implementation
"""
import logging
from typing import Any, List, Optional, Union

import redis.asyncio as redis
from redis.asyncio import Redis

from src.cache.backends.base import CacheBackend
from src.core.config import settings


logger = logging.getLogger(__name__)


class RedisBackend(CacheBackend):
    """
    Redis cache backend implementation
    """
    
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        
    async def init(self) -> None:
        """Initialize Redis connection pool"""
        logger.info("Initializing Redis connection pool")
        self._pool = redis.ConnectionPool.from_url(
            url=str(settings.REDIS_URI),
            max_connections=10,
            decode_responses=True,
        )
    
    async def close(self) -> None:
        """Close Redis connection pool"""
        if self._pool:
            logger.info("Closing Redis connection pool")
            await self._pool.disconnect()
            self._pool = None
    
    async def _get_conn(self) -> Redis:
        """Get a Redis client from the connection pool"""
        if not self._pool:
            await self.init()
        return redis.Redis(connection_pool=self._pool)
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis"""
        try:
            client = await self._get_conn()
            return await client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {str(e)}")
            return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a value in Redis"""
        try:
            client = await self._get_conn()
            return await client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error: {str(e)}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis"""
        if not keys:
            return 0
            
        try:
            client = await self._get_conn()
            return await client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error: {str(e)}")
            return 0
    
    async def scan(self, cursor: Any, match: str, count: int) -> tuple[Any, List[str]]:
        """Scan Redis for keys matching a pattern"""
        try:
            client = await self._get_conn()
            return await client.scan(cursor=cursor, match=match, count=count)
        except Exception as e:
            logger.error(f"Redis SCAN error: {str(e)}")
            return cursor, []
    
    async def flush(self) -> bool:
        """Clear all cached data in Redis"""
        try:
            client = await self._get_conn()
            await client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {str(e)}")
            return False
