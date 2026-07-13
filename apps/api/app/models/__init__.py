"""Persistence models (SQLAlchemy 2 ORM).

Import every model module here so that ``Base.metadata`` is fully populated for
Alembic autogenerate. Example (once you add models)::

    from app.models.equipment import Equipment  # noqa: F401
"""

from app.models.base import Base

__all__ = ["Base"]
