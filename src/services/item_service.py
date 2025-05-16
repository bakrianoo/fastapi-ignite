"""
Service layer for Item operations
"""
import logging
import uuid
from typing import List, Optional, Union

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ResourceNotFoundError
from src.db.models.item import Item
from src.schemas.item import ItemCreate, ItemUpdate


logger = logging.getLogger(__name__)


class ItemService:
    """
    Service class for item operations
    """
    
    @staticmethod
    async def create_item(
        db: AsyncSession, item_data: ItemCreate
    ) -> Item:
        """
        Create a new item
        """
        item = Item(**item_data.model_dump())
        db.add(item)
        await db.flush()
        await db.refresh(item)
        logger.info(f"Created item: {item.id}")
        return item
    
    @staticmethod
    async def get_item(
        db: AsyncSession, item_id: uuid.UUID
    ) -> Item:
        """
        Get an item by ID
        """
        query = select(Item).where(Item.id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if item is None:
            logger.warning(f"Item not found: {item_id}")
            raise ResourceNotFoundError("Item", item_id)
        
        return item
    
    @staticmethod
    async def get_items(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100, 
        active_only: bool = False
    ) -> List[Item]:
        """
        Get multiple items with pagination
        """
        query = select(Item)
        
        if active_only:
            query = query.where(Item.is_active == True)
        
        query = query.offset(skip).limit(limit).order_by(Item.created_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items)
    
    @staticmethod
    async def update_item(
        db: AsyncSession, 
        item_id: uuid.UUID, 
        item_data: ItemUpdate
    ) -> Item:
        """
        Update an item
        """
        # First check if the item exists
        item = await ItemService.get_item(db, item_id)
        
        # Filter out None values
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        
        if not update_data:
            # No updates to apply
            return item
        
        # Update the item
        stmt = (
            update(Item)
            .where(Item.id == item_id)
            .values(**update_data)
            .returning(Item)
        )
        
        result = await db.execute(stmt)
        updated_item = result.scalar_one()
        logger.info(f"Updated item: {item_id}")
        
        return updated_item
    
    @staticmethod
    async def delete_item(
        db: AsyncSession, 
        item_id: uuid.UUID
    ) -> None:
        """
        Delete an item
        """
        # First check if the item exists
        await ItemService.get_item(db, item_id)
        
        # Delete the item
        stmt = delete(Item).where(Item.id == item_id)
        await db.execute(stmt)
        logger.info(f"Deleted item: {item_id}")
        
    @staticmethod
    async def search_items(
        db: AsyncSession, 
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Item]:
        """
        Search items by name or description
        """
        search_pattern = f"%{search_term}%"
        
        query = (
            select(Item)
            .where(
                (Item.name.ilike(search_pattern)) | 
                (Item.description.ilike(search_pattern))
            )
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items)
