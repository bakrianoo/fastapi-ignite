"""
Tests for Item service functions
"""
import uuid
from unittest import mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ResourceNotFoundError
from src.db.models.item import Item
from src.schemas.item import ItemCreate, ItemUpdate
from src.services.item_service import ItemService


@pytest.mark.asyncio
async def test_create_item_service(test_db: AsyncSession) -> None:
    """
    Test creating an item via the service layer
    """
    # Create item data
    item_data = ItemCreate(
        name="Service Test Item",
        description="Item created in service test",
        is_active=True
    )
    
    # Call service method
    item = await ItemService.create_item(test_db, item_data)
    
    # Verify item
    assert item.name == item_data.name
    assert item.description == item_data.description
    assert item.is_active == item_data.is_active
    assert item.id is not None


@pytest.mark.asyncio
async def test_get_item_service(test_db: AsyncSession) -> None:
    """
    Test getting an item via the service layer
    """
    # Create test item
    item = Item(name="Get Service Item", description="Test get service", is_active=True)
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    
    # Get the item
    retrieved_item = await ItemService.get_item(test_db, item.id)
    
    # Verify
    assert retrieved_item.id == item.id
    assert retrieved_item.name == item.name


@pytest.mark.asyncio
async def test_get_nonexistent_item_service(test_db: AsyncSession) -> None:
    """
    Test getting a non-existent item raises the correct exception
    """
    # Generate random UUID
    random_id = uuid.uuid4()
    
    # Attempt to get non-existent item
    with pytest.raises(ResourceNotFoundError):
        await ItemService.get_item(test_db, random_id)


@pytest.mark.asyncio
async def test_update_item_service(test_db: AsyncSession) -> None:
    """
    Test updating an item via the service layer
    """
    # Create test item
    item = Item(name="Update Service Item", description="Original description", is_active=True)
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    
    # Update data
    update_data = ItemUpdate(
        name="Updated Service Item",
        description="Updated service description",
        is_active=True
    )
    
    # Update item
    updated_item = await ItemService.update_item(test_db, item.id, update_data)
    
    # Verify
    assert updated_item.name == update_data.name
    assert updated_item.description == update_data.description
    assert updated_item.id == item.id


@pytest.mark.asyncio
async def test_delete_item_service(test_db: AsyncSession) -> None:
    """
    Test deleting an item via the service layer
    """
    # Create test item
    item = Item(name="Delete Service Item", description="To be deleted", is_active=True)
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    
    # Delete item
    await ItemService.delete_item(test_db, item.id)
    
    # Verify deletion
    with pytest.raises(ResourceNotFoundError):
        await ItemService.get_item(test_db, item.id)


@pytest.mark.asyncio
async def test_search_items_service(test_db: AsyncSession) -> None:
    """
    Test searching items via the service layer
    """
    # Create items with searchable content
    items = [
        Item(name="Search Service Widget", description="A searchable service item", is_active=True),
        Item(name="Another Item", description="Has search service term", is_active=True),
        Item(name="Unrelated Item", description="Should not match", is_active=True),
    ]
    
    for item in items:
        test_db.add(item)
    
    await test_db.commit()
    
    # Search for items
    search_results = await ItemService.search_items(test_db, "search service")
    
    # Verify
    assert len(search_results) == 2
    names = [item.name for item in search_results]
    assert "Search Service Widget" in names
    assert "Another Item" in names
    assert "Unrelated Item" not in names
