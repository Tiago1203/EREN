# app/core

**Cross-cutting infrastructure** shared across the application:

- `database.py` — SQLAlchemy 2 async engine, session factory and the `get_db`
  FastAPI dependency (lazily initialized).
- `logging.py` — centralized logging configuration (`configure_logging`).
- `exceptions.py` — base `AppError` type and `install_exception_handlers` for
  consistent JSON error responses.

This layer is imported by `services`, `routers` and `main`; it must not depend
on them.
