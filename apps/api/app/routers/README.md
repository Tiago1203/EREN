# app/routers

**HTTP presentation layer** — FastAPI `APIRouter`s that expose the API.

- Each resource gets its own module (e.g. `health.py`).
- `__init__.py` aggregates them into `api_router`, which `app.main` mounts under
  the configured API prefix (`/api/v1`).
- Routers should be thin: validate input via `schemas`, delegate work to
  `services`, and return `schemas`. Keep business logic out of this layer.

Only a `/health` liveness probe exists today — no business endpoints yet.
