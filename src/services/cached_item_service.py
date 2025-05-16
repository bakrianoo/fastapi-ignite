"""
Example service using the cache system
"""
import json
import logging
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import CacheBackend, cached, invalidate_cache
from src.db.models.item import Item
from src.schemas.item import ItemCreate, ItemUpdate


logger = logging.getLogger(__name__)


class CachedItemService:
    """
    Service class demonstrating the use of different cache backends
    """
    
    @staticmethod
    @cached(ttl=300, key_prefix="item")
    async def get_item_by_id(
        db: AsyncSession, 
        item_id: uuid.UUID
    ) -> Optional[dict]:
        """
        Get an item by ID with caching
        """
        query = select(Item).where(Item.id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if item is None:
            return None
            
        # Return a dict so it can be JSON serialized for cache
        return {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "status": item.status,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }
        
    @staticmethod
    @invalidate_cache(key_pattern="item:*")
    async def update_item(
        db: AsyncSession,
        item_id: uuid.UUID,
        item_data: ItemUpdate
    ) -> Item:
        """
        Update an item and invalidate cache
        """
        query = select(Item).where(Item.id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if item is None:
            raise ValueError(f"Item not found: {item_id}")
            
        # Update item attributes
        for key, value in item_data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
            
        await db.commit()
        await db.refresh(item)
        
        logger.info(f"Updated item: {item.id}")
        return item
        
    @staticmethod
    async def direct_cache_example(
        db: AsyncSession,
        cache: CacheBackend,
        item_id: uuid.UUID
    ) -> dict:
        """
        Example using the cache backend directly
        """
        # Create cache key
        cache_key = f"direct:item:{item_id}"
        
        # Try to get from cache first
        cached_value = await cache.get(cache_key)
        if cached_value:
            logger.info(f"Cache hit for item: {item_id}")
            return json.loads(cached_value)
            
        # Not in cache, get from database
        logger.info(f"Cache miss for item: {item_id}")
        query = select(Item).where(Item.id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if item is None:
            return None
            
        # Create serializable result
        item_data = {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "status": item.status,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }
        
        # Store in cache for future requests
        await cache.set(
            cache_key,
            json.dumps(item_data),
            ex=300  # 5 minutes
        )
        
        return item_data
