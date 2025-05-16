# Cache Configuration

Rankyx  FastAPI Boilerplate  supports multiple cache backends that can be configured through environment variables
or the configuration files.

## Available Cache Backends

- **Redis**: Redis server-based caching (default)
- **File**: Persistent file-based caching
- **Memory**: In-memory caching (not persistent across restarts)

## Configuration Options

The following settings can be configured in your `.env` file or environment variables:

```
# Cache backend type (redis, file, memory)
CACHE_BACKEND_TYPE=redis

# Cache TTL in seconds
CACHE_TTL_SECONDS=300

# Path for file-based cache (relative to project root)
CACHE_FILE_PATH=cache
```

## Usage Examples

### Caching Function Results

```python
from src.cache.decorators import cached

@cached(ttl=60, key_prefix="user")
async def get_user_data(user_id: int):
    # Function logic here
    return data
```

### Invalidating Cache

```python
from src.cache.decorators import invalidate_cache

@invalidate_cache(key_pattern="user:*")
async def update_user(user_id: int, data: dict):
    # Update logic here
    return updated_user
```

### Using Cache Directly in FastAPI Endpoints

```python
from fastapi import APIRouter, Depends
from src.cache import CacheBackend, get_cache

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(item_id: int, cache: CacheBackend = Depends(get_cache)):
    # Try to get from cache
    cache_key = f"item:{item_id}"
    cached_item = await cache.get(cache_key)
    
    if cached_item:
        return json.loads(cached_item)
        
    # Get from database if not cached
    item = await item_service.get_item(item_id)
    
    # Store in cache
    await cache.set(cache_key, json.dumps(item), ex=300)
    
    return item
```
