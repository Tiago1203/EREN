# app/models

**Persistence layer** — SQLAlchemy 2 ORM entities.

- `base.py` — the shared `DeclarativeBase` (`Base`) with a constraint naming
  convention for stable Alembic diffs.
- Define one module per entity and import it in `__init__.py` so
  `Base.metadata` is complete for Alembic autogenerate.

No entities are defined yet.
