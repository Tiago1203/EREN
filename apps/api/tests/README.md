# tests

**Pytest** suite for the API.

- `conftest.py` — shared fixtures (e.g. a FastAPI `TestClient`).
- `test_health.py` — smoke test proving the app is wired together.

Run from `apps/api/`:

```bash
uv run pytest
```

`pytest.ini_options` (in `pyproject.toml`) sets `pythonpath = ["."]` and
`asyncio_mode = "auto"` so `app` imports resolve and async tests run without
extra decorators.
