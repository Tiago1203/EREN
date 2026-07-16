"""Smoke test proving the app is wired together (routers, prefix, middleware).

NOTE: This test is skipped until EPIC-1 (Foundation) is complete.
It requires the full app wiring (routers, auth provider, database).
"""

import pytest


@pytest.mark.skip(reason="Requires full app wiring (routers, auth provider) — complete in EPIC-1")
def test_health_ok() -> None:
    """Test the /api/v1/health endpoint when app is fully wired."""
    from fastapi.testclient import TestClient

    from app.main import create_app

    client = TestClient(create_app())
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "EREN API"
    assert "X-Request-ID" in response.headers
