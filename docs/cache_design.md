# Cache System Design

This document outlines the design and implementation of the cache system in the FastAPI-Ignite FastAPI Boilerplate .

## Overview

The cache system is designed using the Strategy pattern, which allows for multiple cache backend implementations to be used interchangeably. The system supports:

1. Redis-based caching
2. File-based caching
3. In-memory caching

## Architecture

The cache system is built around the following components:

### Core Components

- **CacheBackend** (Abstract Base Class): Defines the interface that all cache backends must implement.
- **RedisBackend**: Implementation using Redis.
- **FileBackend**: Implementation using file system.
- **MemoryBackend**: Implementation using in-memory dictionaries.
- **Cache Factory**: Creates and manages the appropriate cache backend.

### Decorator-based Caching

The system provides decorators for easy caching of function results:

- `@cached`: Caches function return values.
- `@invalidate_cache`: Invalidates cache entries matching a pattern.

### Direct Cache Usage

Endpoints and services can directly access the cache backend through dependency injection.

## Configuration

The cache system is configurable through the following settings:

- **CACHE_BACKEND_TYPE**: The type of cache backend to use ("redis", "file", "memory").
- **CACHE_TTL_SECONDS**: Default time-to-live for cache entries.
- **CACHE_FILE_PATH**: Path for file-based cache (when using "file" backend).

These can be configured in:
- `.env` file
- TOML configuration files
- Environment variables

## Usage Examples

### Caching Function Results

```python
from src.cache import cached

@cached(ttl=300, key_prefix="user")
async def get_user(user_id: int):
    # Function logic
    return user_data
```

### Invalidating Cache

```python
from src.cache import invalidate_cache

@invalidate_cache(key_pattern="user:*")
async def update_user(user_id: int, data: dict):
    # Update logic
    return updated_user
```

### Direct Cache Access

```python
from src.cache import CacheBackend, get_cache

@router.get("/items/{item_id}")
async def get_item(
    item_id: int, 
    cache: CacheBackend = Depends(get_cache)
):
    cache_key = f"item:{item_id}"
    
    # Try to get from cache
    cached_value = await cache.get(cache_key)
    if cached_value:
        return json.loads(cached_value)
        
    # Get from database
    item = await db_get_item(item_id)
    
    # Store in cache
    await cache.set(cache_key, json.dumps(item), ex=300)
    return item
```

## Best Practices

1. Use consistent cache key naming conventions.
2. Set appropriate TTL values based on data volatility.
3. Implement proper cache invalidation strategies.
4. Use the appropriate backend based on deployment needs.
