"""Department domain entities."""

from core.department.domain.entities.department import (
    Department,
    DepartmentStatus,
    DepartmentType,
)
from core.department.domain.entities.unit import Unit, UnitStatus, UnitType

__all__ = [
    "Department",
    "DepartmentStatus",
    "DepartmentType",
    "Unit",
    "UnitStatus",
    "UnitType",
]
