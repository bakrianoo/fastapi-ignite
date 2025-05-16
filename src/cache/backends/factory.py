"""
Cache backend factory
"""
import logging
from enum import Enum
from typing import Optional

from src.cache.backends.base import CacheBackend
from src.cache.backends.redis import RedisBackend
from src.cache.backends.file import FileBackend
from src.cache.backends.memory import MemoryBackend
from src.core.config import settings


logger = logging.getLogger(__name__)


class CacheBackendType(str, Enum):
    """Enum of supported cache backends"""
    REDIS = "redis"
    FILE = "file"
    MEMORY = "memory"


# Singleton cache instance
_cache_instance: Optional[CacheBackend] = None


def get_cache_backend() -> CacheBackend:
    """
    Get or create the singleton cache backend instance
    
    Returns:
        The appropriate cache backend based on configuration
    """
    global _cache_instance
    
    if _cache_instance is None:
        backend_type = settings.CACHE_BACKEND_TYPE
        
        if backend_type == CacheBackendType.REDIS:
            logger.info("Using Redis cache backend")
            _cache_instance = RedisBackend()
        elif backend_type == CacheBackendType.FILE:
            logger.info("Using file-based cache backend")
            _cache_instance = FileBackend()
        elif backend_type == CacheBackendType.MEMORY:
            logger.info("Using in-memory cache backend")
            _cache_instance = MemoryBackend()
        else:
            logger.warning(f"Unknown cache backend type '{backend_type}', falling back to in-memory cache")
            _cache_instance = MemoryBackend()
    
    return _cache_instance


async def init_cache_backend() -> None:
    """Initialize the cache backend"""
    backend = get_cache_backend()
    await backend.init()


async def close_cache_backend() -> None:
    """Close the cache backend"""
    global _cache_instance
    
    if _cache_instance is not None:
        await _cache_instance.close()
        _cache_instance = None
