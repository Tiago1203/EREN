# @eren/api (FastAPI)

The **programmatic gateway** into EREN — an HTTP API built with FastAPI,
following a clean, layered architecture.

> **Status:** professional skeleton. Wiring is in place (config, logging,
> middleware, error handling, DB layer, migrations, tests). The only endpoint is
> a `/health` liveness probe — **no business endpoints, AI, or agents yet.**

## Stack

| Concern | Tool |
| --- | --- |
| Language | Python 3.12 |
| Web framework | FastAPI |
| Packaging / envs | uv |
| Validation / settings | Pydantic v2 + pydantic-settings |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Lint / format | Ruff |
| Tests | Pytest |

## Layout (clean architecture)

```
apps/api/
├── app/
│   ├── config/       # Typed settings (env-driven)
│   ├── core/         # Infra: database, logging, exceptions
│   ├── middleware/   # ASGI/HTTP middleware
│   ├── models/       # SQLAlchemy ORM entities + declarative Base
│   ├── routers/      # HTTP presentation layer (FastAPI routers)
│   ├── schemas/      # Pydantic v2 request/response DTOs
│   ├── services/     # Application/use-case layer (business logic)
│   └── main.py       # App factory (create_app)
├── migrations/       # Alembic environment + versions
├── tests/            # Pytest suite
├── alembic.ini
└── pyproject.toml
```

**Dependency direction:** `routers → services → models`, with `schemas` as the
data contract and `core`/`config` as shared infrastructure. Inner layers never
import outer layers (e.g. `services` must not import `routers`).

## Develop

From `apps/api/`:

```bash
uv sync                                   # create venv + install deps (incl. dev)
uv run uvicorn app.main:app --reload      # run the API (http://localhost:8000)
uv run ruff check .                        # lint
uv run ruff format .                       # format
uv run pytest                              # tests
```

Health check: `GET /api/v1/health` → `{"status":"ok", ...}`.

## Migrations (Alembic)

The DB URL is taken from app settings (`EREN_API_DATABASE_URL`); Alembic derives
a synchronous URL automatically.

```bash
uv run alembic revision --autogenerate -m "create initial tables"
uv run alembic upgrade head
```

## Configuration

Copy `.env.example` → `.env`. All variables use the `EREN_API_` prefix (see
`app/config/settings.py`).
