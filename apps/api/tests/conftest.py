"""Shared pytest fixtures for the EREN API test suite."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A synchronous test client backed by a fresh app instance."""
    with TestClient(create_app()) as test_client:
        yield test_client
