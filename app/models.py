"""
Pydantic Models for API Request/Response
=========================================
This module defines Pydantic models used for:
- Request validation (input data)
- Response serialization (output data)
- Type safety in API endpoints

These models are separate from database models (in database.py) and provide
a clean API layer that can evolve independently from the database schema.
"""

from pydantic import BaseModel
from typing import List, Optional
from fastapi_users import schemas
from datetime import datetime
import uuid


# ============================================================================
# Item Models
# ============================================================================

class ItemBase(BaseModel):
    """
    Base model for items.
    Can be extended with common fields shared across item models.
    """
    pass


class ItemCreate(ItemBase):
    """
    Model for creating new items.
    Defines required fields when creating an item via API.
    """
    pass


class Item(ItemBase):
    """
    Base item model for API responses.
    Includes timestamps and ID from database.
    """
    id: uuid.UUID
    time_created:  Optional[datetime]  # When item was created
    time_updated: Optional[datetime]    # When item was last updated

    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy models


class ItemOwned(Item):
    """
    Item model including owner information.
    Used when returning items with their owners.
    """
    owners: Optional[List['UserRead']] = []


class ItemAvailable(Item):
    """
    Item model including access information.
    Used when returning items with users who have access.
    """
    accessible_to: Optional[List['UserRead']] = []


# ============================================================================
# User Models
# ============================================================================

class UserRead(schemas.BaseUser[uuid.UUID]):
    """
    User model for API responses.
    Extends FastAPI Users base schema with UUID type.
    """
    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy models


class UserWithItems(UserRead):
    """
    Extended user model including owned and accessible items.
    Used when returning user data with their associated items.
    """
    items_owned: Optional[List['Item']] = []        # Items the user owns
    items_available: Optional[List['Item']] = []    # Items the user can access


class UserCreate(schemas.BaseUserCreate):
    """
    Model for creating new users.
    Extends FastAPI Users base create schema.
    """
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """
    Model for updating existing users.
    Extends FastAPI Users base update schema.
    """
    pass


# ============================================================================
# Forward Reference Resolution
# ============================================================================
# Resolves forward references in models that reference each other.
# Required when models have circular or forward references.
# ============================================================================
UserWithItems.update_forward_refs()
ItemOwned.update_forward_refs()
ItemAvailable.update_forward_refs()

