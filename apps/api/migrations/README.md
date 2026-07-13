# migrations

**Alembic** database migrations for the EREN API.

- `env.py` — wires Alembic to app settings (`EREN_API_DATABASE_URL`, converted
  to a sync URL) and `app.models.base.Base.metadata`.
- `script.py.mako` — template for generated revision files.
- `versions/` — individual migration scripts (empty until the first model).

Usage (from `apps/api/`):

```bash
uv run alembic revision --autogenerate -m "create initial tables"
uv run alembic upgrade head
uv run alembic downgrade -1
```
