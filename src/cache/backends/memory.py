"""
In-memory cache backend implementation
"""
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union

from src.cache.backends.base import CacheBackend


logger = logging.getLogger(__name__)


class MemoryBackend(CacheBackend):
    """
    In-memory cache backend implementation
    
    Stores cache entries in a dictionary in memory
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
    async def init(self) -> None:
        """Initialize the memory cache"""
        logger.info("Initializing in-memory cache")
        self._cache = {}
    
    async def close(self) -> None:
        """Close the memory cache"""
        logger.info("Closing in-memory cache")
        self._cache = {}
    
    async def _check_expiry(self, key: str) -> bool:
        """
        Check if a key is expired and remove it if so
        
        Returns True if the key exists and is not expired
        """
        if key not in self._cache:
            return False
            
        entry = self._cache[key]
        expiry = entry.get('expiry')
        
        if expiry is not None and time.time() > expiry:
            # Key is expired, remove it
            del self._cache[key]
            return False
            
        return True
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from the memory cache"""
        try:
            async with self._lock:
                # Check if key exists and is not expired
                if await self._check_expiry(key):
                    return self._cache[key]['value']
                return None
        except Exception as e:
            logger.error(f"Memory cache GET error: {str(e)}")
            return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a value in the memory cache"""
        try:
            entry = {
                'value': value,
                'created': time.time(),
            }
            
            if ex is not None:
                entry['expiry'] = time.time() + ex
                
            async with self._lock:
                self._cache[key] = entry
                
            return True
        except Exception as e:
            logger.error(f"Memory cache SET error: {str(e)}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from the memory cache"""
        if not keys:
            return 0
            
        deleted = 0
        
        try:
            async with self._lock:
                for key in keys:
                    if key in self._cache:
                        del self._cache[key]
                        deleted += 1
                        
            return deleted
        except Exception as e:
            logger.error(f"Memory cache DELETE error: {str(e)}")
            return deleted
    
    async def scan(self, cursor: Any, match: str, count: int) -> tuple[Any, List[str]]:
        """Scan the memory cache for keys matching a pattern"""
        try:
            import fnmatch
            
            # Use cursor as an offset
            cursor = int(cursor) if cursor and cursor != b"0" else 0
            
            async with self._lock:
                # Get all keys, checking expiry at the same time
                valid_keys = []
                for key in list(self._cache.keys()):
                    if await self._check_expiry(key):
                        valid_keys.append(key)
                
                # Filter by pattern
                filtered_keys = [k for k in valid_keys if fnmatch.fnmatch(k, match)]
                
                # Apply pagination
                end_idx = min(cursor + count, len(filtered_keys))
                result_keys = filtered_keys[cursor:end_idx]
                
                # Calculate next cursor
                next_cursor = str(end_idx) if end_idx < len(filtered_keys) else "0"
                
                return next_cursor, result_keys
        except Exception as e:
            logger.error(f"Memory cache SCAN error: {str(e)}")
            return "0", []
    
    async def flush(self) -> bool:
        """Clear all cached data in the memory cache"""
        try:
            async with self._lock:
                self._cache.clear()
            return True
        except Exception as e:
            logger.error(f"Memory cache FLUSH error: {str(e)}")
            return False
