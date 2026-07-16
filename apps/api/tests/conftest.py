"""Shared pytest fixtures for the EREN API test suite."""

import os
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import all models to register them with Base.metadata
from app.infrastructure.models import (  # noqa: F401
    ActionModel,
    ConversationMessageModel,
    DeviceModel,
    DomainEventModel,
    EvidenceModel,
    IncidentModel,
    InvestigationModel,
    KnowledgeArticleModel,
    RecommendationModel,
)
from app.models import Base

# Build test DB URL from the same postgres instance but different database
_test_db_url = os.environ.get(
    "EREN_API_DATABASE_URL",
    "postgresql+asyncpg://eren:eren@localhost:5432/eren"
)
# Use eren_test database for integration tests (same user/pass as main DB)
_test_db_url = _test_db_url.replace("/eren", "/eren_test")
# Ensure we use the eren user/pass even if connecting to eren_test database
if "eren_test" in _test_db_url and "eren:eren@" in _test_db_url:
    # Already using eren user, which is correct
    pass
else:
    _test_db_url = _test_db_url.replace("eren_test:eren", "eren:eren")


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
    """Create async engine for integration tests.

    Connects to eren_test database. Creates all schemas, drops and recreates
    all tables before each test to ensure a clean state.
    """
    engine = create_async_engine(_test_db_url, echo=False)

    # All schemas used by infrastructure models
    schemas = ["device", "incident", "knowledge", "recommendation", "public"]

    async with engine.begin() as conn:
        for schema in schemas:
            await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            await conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            await conn.execute(text(f'GRANT ALL ON SCHEMA "{schema}" TO eren'))

    # Now create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        for schema in schemas:
            await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))

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
