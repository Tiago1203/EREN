"""Shared pytest fixtures for the EREN API test suite."""

from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_repository():
    """Mock PatientRepository for unit tests."""
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    """Mock EventBus for unit tests."""
    return AsyncMock()
