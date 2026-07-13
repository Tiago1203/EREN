# @eren/api (FastAPI)

The **programmatic gateway** into EREN — an HTTP API built with FastAPI.

> **Status:** scaffolded, not implemented. Only boilerplate and a `/health`
> placeholder exist. No business logic, AI, or agents live here yet.

## Layout

- `app/main.py` — FastAPI application entrypoint (placeholder).
- `app/__init__.py` — application package marker.
- `requirements.txt` — Python dependencies.
- `pyproject.toml` — package metadata / build config.
- `.env.example` — sample environment variables.

## Develop

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API composes capability from `core/*` and shared contracts from
`packages/schemas`. Keep transport concerns here; keep cognition in `core/`.
