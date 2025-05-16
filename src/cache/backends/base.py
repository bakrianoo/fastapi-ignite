"""
Base cache backend abstract class
"""
import abc
from typing import Any, Dict, List, Optional, Union


class CacheBackend(abc.ABC):
    """
    Abstract base class for cache backends
    
    All cache implementations must extend this class and implement its methods
    """
    
    @abc.abstractmethod
    async def init(self) -> None:
        """Initialize the cache backend"""
        pass
    
    @abc.abstractmethod
    async def close(self) -> None:
        """Close the cache backend"""
        pass
    
    @abc.abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            The cached string value or None if not found
        """
        pass
    
    @abc.abstractmethod
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """
        Set a value in the cache
        
        Args:
            key: Cache key
            value: Value to store (string)
            ex: Expiration time in seconds
            
        Returns:
            True if successful
        """
        pass
    
    @abc.abstractmethod
    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys from the cache
        
        Args:
            keys: One or more keys to delete
            
        Returns:
            Number of keys deleted
        """
        pass
    
    @abc.abstractmethod
    async def scan(self, cursor: Any, match: str, count: int) -> tuple[Any, List[str]]:
        """
        Scan the cache for keys matching a pattern
        
        Args:
            cursor: Cursor for pagination
            match: Pattern to match
            count: Number of items to return per batch
            
        Returns:
            A tuple of (next_cursor, keys)
        """
        pass
    
    @abc.abstractmethod
    async def flush(self) -> bool:
        """
        Clear all cached data
        
        Returns:
            True if successful
        """
        pass
