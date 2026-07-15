"""Persistence models (SQLAlchemy 2 ORM).

Import every model module here so that ``Base.metadata`` is fully populated for
Alembic autogenerate.
"""

from app.models.base import Base
from app.models.diagnosis import Diagnosis
from app.models.patient import Patient

__all__ = ["Base", "Diagnosis", "Patient"]
