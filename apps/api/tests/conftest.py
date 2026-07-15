"""Shared pytest fixtures for the EREN API test suite."""

import os
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

# Use test database URL from environment or default
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://eren:eren_test@localhost:5432/eren_test"
)


@pytest.fixture
def mock_repository():
    """Mock PatientRepository for unit tests."""
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    """Mock EventBus for unit tests."""
    return AsyncMock()


@pytest_asyncio.fixture
async def db_engine():
    """Create async engine for integration tests."""
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Create async session for integration tests."""
    async_session_factory = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()
