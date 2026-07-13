"""Smoke test proving the app is wired together (routers, prefix, middleware)."""

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "EREN API"
    assert "X-Request-ID" in response.headers
