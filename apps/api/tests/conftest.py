"""Shared pytest fixtures for the EREN API test suite."""

from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_repository():
    """Mock PatientRepository for unit tests."""
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    """Mock EventBus for unit tests."""
    return AsyncMock()
