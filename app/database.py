"""
Database Configuration and Models
==================================
This module configures the SQLAlchemy database connection and defines the
database models for users, items, and access tokens.

Uses:
- PostgreSQL database (async connection via asyncpg)
- SQLAlchemy ORM with async support
- FastAPI Users for authentication and user management
- UUID-based primary keys for users
- Many-to-many relationships for item ownership and access control
"""

from fastapi import Depends
from typing import AsyncGenerator, List
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTableUUID,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Mapped, DeclarativeBase
from sqlalchemy import Column, ForeignKey, Table, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
import os

# ============================================================================
# Database Connection Configuration
# ============================================================================
# Constructs async PostgreSQL connection URL from environment variables.
# Format: postgresql+asyncpg://user:password@host:port/database
# ============================================================================
DATABASE_URL_ASYNC = "postgresql+asyncpg://" + os.environ['POSTGRES_USER'] + ":" + os.environ['POSTGRES_PASSWORD'] +\
               "@db:" + os.environ['POSTGRES_PORT'] + "/" + os.environ['POSTGRES_DB']

# Create async database engine
engine = create_async_engine(DATABASE_URL_ASYNC)

# Create session factory for async database sessions
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class for all database models
class Base(DeclarativeBase):
    pass


# ============================================================================
# Association Tables (Many-to-Many Relationships)
# ============================================================================
# These tables manage the many-to-many relationships between users and items:
# - ItemOwner: Tracks which users own which items
# - ItemAccess: Tracks which users have access to which items (separate from ownership)
# ============================================================================

# Item Ownership Association Table
# Links items to their owners (users who created/own the item)
ItemOwner = Table('itemowner',
                  Base.metadata,
                  Column('itemId', Integer, ForeignKey('items.id'), primary_key=True),
                  Column('userId', UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True),
                  Column('time_created', DateTime(timezone=True), server_default=func.now()),
                  Column('time_updated', DateTime(timezone=True), onupdate=func.now()),
                  )

# Item Access Association Table
# Links items to users who have been granted access (but may not own the item)
ItemAccess = Table('itemaccess',
                   Base.metadata,
                   Column('itemId', Integer, ForeignKey('items.id'), primary_key=True),
                   Column('userId', UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True),
                   Column('time_created', DateTime(timezone=True), server_default=func.now()),
                   Column('time_updated', DateTime(timezone=True), onupdate=func.now()),
                   )


# ============================================================================
# Database Models
# ============================================================================

class ItemTable(Base):
    """
    Item/Shipment Model
    ===================
    Represents an item or shipment in the system.
    Each item can have multiple owners and can grant access to multiple users.
    """
    __tablename__ = "items"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    text: Mapped[str] = Column(Text, nullable=False)  # Item description/content
    # Many-to-many: Users who own this item
    owners: Mapped[List['User']] = relationship("User", secondary=ItemOwner, back_populates="items_owned", lazy='selectin')
    # Many-to-many: Users who have access to this item
    access_granted: Mapped[List['User']] = relationship("User", secondary=ItemAccess, back_populates="items_available", lazy='selectin')


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    User Model
    ==========
    Extends FastAPI Users base model with UUID primary key.
    Includes relationships to items the user owns and items they can access.
    """
    # Many-to-many: Items this user owns
    items_owned: Mapped[List[ItemTable]] = relationship("ItemTable", secondary=ItemOwner, back_populates="owners", lazy='selectin')
    # Many-to-many: Items this user can access (but may not own)
    items_available: Mapped[List[ItemTable]] = relationship("ItemTable", secondary=ItemAccess, back_populates="access_granted", lazy='selectin')


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    """
    Access Token Model
    ==================
    Stores authentication tokens for users.
    Used by FastAPI Users for session management and API authentication.
    """
    pass


# ============================================================================
# Database Initialization and Dependency Functions
# ============================================================================

async def create_db_and_tables():
    """
    Create all database tables.
    Should be called on application startup to ensure tables exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that provides a database session.
    Used by FastAPI dependency injection system.
    
    Yields:
        AsyncSession: Database session for querying
    """
    async with SessionLocal() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency function that provides a user database adapter.
    Required by FastAPI Users for user management operations.
    
    Args:
        session: Database session from get_async_session()
    
    Yields:
        SQLAlchemyUserDatabase: User database adapter
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(session: AsyncSession = Depends(get_async_session),):
    """
    Dependency function that provides an access token database adapter.
    Required by FastAPI Users for token management.
    
    Args:
        session: Database session from get_async_session()
    
    Yields:
        SQLAlchemyAccessTokenDatabase: Access token database adapter
    """
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)