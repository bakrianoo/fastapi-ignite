"""
Pydantic schemas for Item objects
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    """
    Base schema for Item data
    """
    name: str = Field(..., description="Item name", max_length=255)
    description: Optional[str] = Field(None, description="Item description")
    is_active: bool = Field(True, description="Whether the item is active")


class ItemCreate(ItemBase):
    """
    Schema for creating a new Item
    """
    pass


class ItemUpdate(BaseModel):
    """
    Schema for updating an existing Item
    """
    name: Optional[str] = Field(None, description="Item name", max_length=255)
    description: Optional[str] = Field(None, description="Item description")
    is_active: Optional[bool] = Field(None, description="Whether the item is active")
    
    # Use Pydantic v2 config
    model_config = ConfigDict(
        extra="forbid",  # Forbid extra fields not defined in model
    )


class ItemInDB(ItemBase):
    """
    Schema for Item data from the database
    """
    id: uuid.UUID = Field(..., description="Item UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Use Pydantic v2 config
    model_config = ConfigDict(
        from_attributes=True,  # Convert ORM model to Pydantic model
    )


class ItemResponse(ItemInDB):
    """
    Schema for Item response data
    """
    pass
