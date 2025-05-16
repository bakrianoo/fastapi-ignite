"""
Tests for the items API endpoints
"""
import uuid
from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.item import Item


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient, test_db: AsyncSession) -> None:
    """
    Test creating a new item through the API
    """
    # Item data
    item_data = {
        "name": "Test Item",
        "description": "This is a test item",
        "is_active": True
    }
    
    # Send request
    response = await client.post(
        "/api/v1/items/",
        json=item_data
    )
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert data["is_active"] == item_data["is_active"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_read_item(client: AsyncClient, test_db: AsyncSession) -> None:
    """
    Test retrieving an item through the API
    """
    # Create a test item in the database
    item = Item(name="Test Get Item", description="Item for testing get", is_active=True)
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    
    # Send request
    response = await client.get(f"/api/v1/items/{item.id}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Get Item"
    assert data["description"] == "Item for testing get"
    assert data["id"] == str(item.id)


@pytest.mark.asyncio
async def test_read_nonexistent_item(client: AsyncClient) -> None:
    """
    Test retrieving a non-existent item
    """
    # Generate a random UUID
    nonexistent_id = uuid.uuid4()
    
    # Send request
    response = await client.get(f"/api/v1/items/{nonexistent_id}")
    
    # Check response
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_item(client: AsyncClient, test_db: AsyncSession) -> None:
    """
    Test updating an item through the API
    """
    # Create a test item in the database
    item = Item(name="Test Update Item", description="Original description", is_active=True)
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    
    # Update data
    update_data = {
        "name": "Updated Name",
        "description": "Updated description"
    }
    
    # Send request
    response = await client.put(
        f"/api/v1/items/{item.id}",
        json=update_data
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["id"] == str(item.id)


@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient, test_db: AsyncSession) -> None:
    """
    Test deleting an item through the API
    """
    # Create a test item in the database
    item = Item(name="Test Delete Item", description="Item to be deleted", is_active=True)
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    
    # Send delete request
    response = await client.delete(f"/api/v1/items/{item.id}")
    
    # Check response
    assert response.status_code == 204
    
    # Verify item is gone
    check_response = await client.get(f"/api/v1/items/{item.id}")
    assert check_response.status_code == 404


@pytest.mark.asyncio
async def test_list_items(client: AsyncClient, test_db: AsyncSession) -> None:
    """
    Test listing items through the API
    """
    # Create multiple test items
    items = [
        Item(name="List Item 1", description="First list item", is_active=True),
        Item(name="List Item 2", description="Second list item", is_active=True),
        Item(name="List Item 3", description="Third list item", is_active=False),
    ]
    
    for item in items:
        test_db.add(item)
    
    await test_db.commit()
    
    # Send request for all items
    response = await client.get("/api/v1/items/")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # There might be other items from previous tests
    
    # Test active_only filter
    response = await client.get("/api/v1/items/?active_only=true")
    assert response.status_code == 200
    data = response.json()
    
    # All returned items should be active
    for item in data:
        assert item["is_active"] == True


@pytest.mark.asyncio
async def test_search_items(client: AsyncClient, test_db: AsyncSession) -> None:
    """
    Test searching items through the API
    """
    # Create items with searchable names/descriptions
    items = [
        Item(name="Special Widget", description="A unique item for search", is_active=True),
        Item(name="Regular Item", description="Contains special keyword", is_active=True),
        Item(name="Another Item", description="Nothing special here", is_active=True),
    ]
    
    for item in items:
        test_db.add(item)
    
    await test_db.commit()
    
    # Search for "special" which should match 2 items
    response = await client.get("/api/v1/items/search/?q=special")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify item names
    names = [item["name"] for item in data]
    assert "Special Widget" in names
