"""
Pytest configuration for the application
"""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)

from src.core.config import settings
from src.db.base import Base
from src.db.session import get_db
from src.main import create_application


# Set test environment
os.environ["ENV"] = "test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an instance of the event loop for each test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_app() -> AsyncGenerator[FastAPI, None]:
    """
    Create a FastAPI test application.
    """
    app = create_application()
    async with LifespanManager(app):
        yield app


@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    """
    Create a test database engine.
    """
    # Create a new test database URL
    TEST_DATABASE_URL = settings.DATABASE_URI.replace(
        f"/{settings.POSTGRES_DB}", "/test_db"
    )
    
    # Create engine for test database
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Dispose engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_app: FastAPI, test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session for a test.
    """
    # Create test session
    connection = await test_db_engine.connect()
    transaction = await connection.begin()
    
    # Use session factory
    test_session_factory = async_sessionmaker(
        connection, expire_on_commit=False
    )
    
    # Create a session
    async with test_session_factory() as session:
        # Override the get_db dependency
        test_app.dependency_overrides[get_db] = lambda: test_session_factory()
        
        yield session
    
    # Rollback the transaction
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing.
    """
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
    ) as client:
        yield client
