"""
Caching decorators for function and API response caching
"""
import functools
import hashlib
import inspect
import json
import logging
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from fastapi import Depends, Request

from src.cache.backends.base import CacheBackend
from src.cache.backends.factory import get_cache_backend
from src.cache.dependencies import get_cache
from src.core.config import settings
from src.core.exceptions import CacheError


logger = logging.getLogger(__name__)


def _get_cache_key(
    prefix: str,
    func_name: str,
    args_dict: Dict[str, Any]
) -> str:
    """
    Generate a cache key from function name and arguments
    """
    # Create a deterministic string representation of args and kwargs
    args_str = json.dumps(args_dict, sort_keys=True)
    
    # Create a hash of the arguments to keep key length reasonable
    args_hash = hashlib.md5(args_str.encode()).hexdigest()
    
    # Combine function name and args hash into a key
    return f"{prefix}:{func_name}:{args_hash}"


def cached(
    ttl: int = None,
    key_prefix: str = "cache",
    key_builder: Callable = None,
    exclude_keys: Tuple[str] = ("self", "cls", "request", "db"),
):
    """
    Decorator for caching function return values in Redis
    
    Args:
        ttl: Time to live in seconds. Defaults to settings.CACHE_TTL_SECONDS.
        key_prefix: Prefix for the cache key to namespace keys
        key_builder: Custom function to build the cache key
        exclude_keys: Parameter names to exclude from key generation
    """    
    def decorator(func):
        # Get function signature for parameter names
        sig = inspect.signature(func)
        func_name = func.__qualname__
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Apply cache dependency if not provided
            cache_backend = kwargs.get("cache")
            if cache_backend is None:
                # Use the singleton cache backend
                cache_backend = get_cache_backend()
                
            # Build a dictionary of all arguments with their parameter names
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            arg_dict = {k: v for k, v in bound_args.arguments.items() 
                        if k not in exclude_keys and not isinstance(v, (CacheBackend, Request))}
            
            # Generate the cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = _get_cache_key(key_prefix, func_name, arg_dict)
            
            # Try to get value from cache
            try:
                cached_value = await cache_backend.get(cache_key)
                if cached_value:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    # Deserialize the cached value from JSON
                    return json.loads(cached_value)
                    
                logger.debug(f"Cache miss for key: {cache_key}")
                # Call the original function
                result = await func(*args, **kwargs)
                
                # Calculate TTL
                actual_ttl = ttl if ttl is not None else settings.CACHE_TTL_SECONDS
                
                # Serialize result to JSON and store in cache
                serialized = json.dumps(result)
                await cache_backend.set(
                    cache_key,
                    serialized,
                    ex=actual_ttl
                )
                
                return result
            except Exception as e:
                # Log the error but don't fail the function
                logger.error(f"Cache error: {str(e)}")
                # Call the original function without caching
                return await func(*args, **kwargs)
                    
        return wrapper
    return decorator


def invalidate_cache(
    key_pattern: str
):
    """
    Decorator for invalidating cache keys matching a pattern
    
    Args:
        key_pattern: Key pattern to match for invalidation (e.g., "user:*")
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache backend
            cache_backend = get_cache_backend()
            
            # Call the original function first
            result = await func(*args, **kwargs)
            
            # Invalidate matching cache keys
            try:
                # Scan for keys matching the pattern
                cursor = "0"
                deleted_count = 0
                
                while cursor:
                    cursor, keys = await cache_backend.scan(
                        cursor=cursor, 
                        match=key_pattern,
                        count=100
                    )
                    
                    if keys:
                        deleted_count += await cache_backend.delete(*keys)
                        logger.debug(f"Invalidated {len(keys)} cache keys")
                    
                    # Stop if we've completed the scan
                    if cursor == "0":
                        break
                
                logger.info(f"Invalidated {deleted_count} cache keys matching '{key_pattern}'")
            except Exception as e:
                logger.error(f"Cache invalidation error: {str(e)}")
                
            return result
        
        return wrapper
    
    return decorator
