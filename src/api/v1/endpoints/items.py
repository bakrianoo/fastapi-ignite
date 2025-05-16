"""
API endpoints for Item resources
"""
import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db_session
from src.cache import CacheBackend, cached, get_cache
from src.core.config import settings
from src.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from src.services.item_service import ItemService
from src.services.cached_item_service import CachedItemService

# Create router with prefix and tags
router = APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Create a new item with the provided information",
)
async def create_item(
    item_data: ItemCreate, 
    db: AsyncSession = Depends(get_db_session),
) -> ItemResponse:
    """
    Create a new item
    """
    item = await ItemService.create_item(db, item_data)
    return item


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get item by ID",
    description="Get detailed information about a specific item by its ID",
)
@cached(ttl=settings.CACHE_TTL_SECONDS, key_prefix="item")
async def get_item(
    item_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db_session),
) -> ItemResponse:
    """
    Get an item by ID with caching
    """
    item = await ItemService.get_item(db, item_id)
    return item


@router.get(
    "/",
    response_model=List[ItemResponse],
    summary="List items",
    description="Get a list of items with optional pagination and filtering",
)
@cached(ttl=60, key_builder=lambda *args, **kwargs: f"items:{kwargs.get('active_only')}:{kwargs.get('skip')}:{kwargs.get('limit')}")
async def list_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max number of items to return"),
    active_only: bool = Query(False, description="Only return active items"),
    db: AsyncSession = Depends(get_db_session),
) -> List[ItemResponse]:
    """
    Get multiple items with pagination and optional filtering
    """
    items = await ItemService.get_items(
        db=db, skip=skip, limit=limit, active_only=active_only
    )
    return items


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Update item",
    description="Update an existing item's information",
)
async def update_item(
    item_id: uuid.UUID,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> ItemResponse:
    """
    Update an item
    """
    updated_item = await ItemService.update_item(db, item_id, item_data)
    return updated_item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item",
    description="Delete an existing item",
)
async def delete_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete an item
    """
    await ItemService.delete_item(db, item_id)


@router.get(
    "/search/",
    response_model=List[ItemResponse],
    summary="Search items",
    description="Search for items by term in name or description",
)
async def search_items(
    q: str = Query(..., min_length=1, description="Search term"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max number of items to return"),
    db: AsyncSession = Depends(get_db_session),
) -> List[ItemResponse]:
    """
    Search for items
    """
    items = await ItemService.search_items(
        db=db, search_term=q, skip=skip, limit=limit
    )
    return items


@router.get(
    "/cached/{item_id}",
    response_model=ItemResponse,
    summary="Get item by ID (using direct cache)",
    description="Get item details using the cache backend directly",
)
async def get_cached_item(
    item_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db_session),
    cache: CacheBackend = Depends(get_cache),
) -> ItemResponse:
    """
    Get an item by ID using the cache backend directly
    
    This endpoint demonstrates how to use the cache backend directly in an endpoint.
    The current cache backend in use is determined by CACHE_BACKEND_TYPE setting.
    """
    # Get item using the direct cache method
    item_data = await CachedItemService.direct_cache_example(db, cache, item_id)
    
    if not item_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found",
        )
        
    return item_data


@router.get(
    "/cache/clear",
    summary="Clear item cache",
    description="Clear all cached items to test cache invalidation",
)
async def clear_item_cache(
    cache: CacheBackend = Depends(get_cache),
) -> dict:
    """
    Clear all item cache entries
    
    This endpoint demonstrates how to manually invalidate cache entries
    by scanning for keys with a pattern and deleting them.
    """
    # Scan for all item cache keys
    cursor = "0"
    deleted_keys = 0
    
    # Scan in batches
    while cursor != "0" or deleted_keys == 0:  # Continue until we complete a full scan
        cursor, keys = await cache.scan(cursor, "item:*", 100)
        
        if keys:
            # Delete found keys
            count = await cache.delete(*keys)
            deleted_keys += count
            
        # Exit if we've completed the scan
        if cursor == "0" and deleted_keys > 0:
            break
            
    return {"message": f"Successfully cleared {deleted_keys} cached items", "deleted_count": deleted_keys}


@router.get(
    "/cache/info",
    summary="Get cache information",
    description="Get information about the current cache configuration",
)
async def get_cache_info() -> dict:
    """
    Get information about the current cache configuration
    
    This endpoint returns details about which cache backend is currently active
    and other relevant configuration.
    """
    return {
        "cache_backend_type": settings.CACHE_BACKEND_TYPE,
        "cache_ttl_seconds": settings.CACHE_TTL_SECONDS,
        "file_cache_path": settings.CACHE_FILE_PATH if settings.CACHE_BACKEND_TYPE == "file" else None,
        "redis_uri": str(settings.REDIS_URI) if settings.CACHE_BACKEND_TYPE == "redis" else None,
    }
