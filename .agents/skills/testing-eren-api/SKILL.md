---
name: testing-eren-api
description: Run and smoke-test the EREN FastAPI backend (apps/api). Use when verifying API changes — that the app boots, routes mount under /api/v1, and endpoints behave as expected.
---

# Testing EREN API (apps/api)

FastAPI backend, clean-architecture skeleton. Python 3.12, managed with **uv**.

## Run it locally
From `apps/api/`:
```bash
uv sync                                          # create .venv + install deps (incl. dev group)
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs` — best for a
  visual/recorded test (execute endpoints from the browser).
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`.

## Checks (all should be green)
```bash
uv run ruff check .            # lint
uv run ruff format --check .   # format
uv run pytest                  # tests (TestClient smoke test)
uv run python -c "from app.main import app"   # import wiring
uv run alembic upgrade head    # migrations env loads (no-op until models exist)
```

## Golden-path smoke test (no auth, no DB needed)
The only endpoint today is the liveness probe. Via Swagger `/docs`:
1. Confirm the title is `EREN API <version>` and the `system` tag lists
   `GET /api/v1/health`.
2. Expand → **Try it out** → **Execute**.
3. Expect **200** and body `{"status":"ok","service":"EREN API","version":"..."}`.
4. Expect an `x-request-id` response header (proves `RequestContextMiddleware`).

Adversarial extras (shell):
```bash
curl -sD - -o /dev/null -H 'X-Request-ID: test-abc-123' \
  http://127.0.0.1:8000/api/v1/health | grep -i x-request-id   # -> echoes test-abc-123
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/health  # -> 404 (prefix required)
```

## Gotchas / future-proofing
- API prefix comes from `EREN_API_API_V1_PREFIX` (default `/api/v1`) — if routes
  seem "missing", they may just be under a different prefix; check settings.
- Settings use the `EREN_API_` env prefix (`app/config/settings.py`); copy
  `.env.example` → `.env` to override (e.g. `EREN_API_DATABASE_URL`).
- Default DB is sqlite (`sqlite+aiosqlite`); the engine is lazy so importing the
  app never needs a live DB. Postgres would use `postgresql+asyncpg://...`.
- If `uv` isn't on PATH: `export PATH="$HOME/.local/bin:$PATH"`.
- Adding models? Import them in `app/models/__init__.py` so Alembic autogenerate
  and `Base.metadata` see them.

## Devin Secrets Needed
- None for the current skeleton (no auth, sqlite default). Future authenticated
  endpoints or a real Postgres would need `EREN_API_DATABASE_URL` and any
  auth/service credentials.
