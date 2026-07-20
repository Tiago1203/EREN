"""Unit entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import AggregateRoot, DepartmentId, OrganizationId, TenantId, UnitId

if TYPE_CHECKING:
    pass


class UnitStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TEMPORARILY_CLOSED = "temporarily_closed"


class UnitType(str, Enum):
    INPATIENT = "inpatient"
    OUTPATIENT = "outpatient"
    EMERGENCY = "emergency"
    OPERATING_ROOM = "operating_room"
    ICU = "icu"


@dataclass(eq=False)
class Unit(AggregateRoot):
    """Unit entity.

    A unit is a sub-division of a department (e.g., ICU-North, ICU-South).
    Units belong to a department.
    """

    tenant_id: TenantId
    organization_id: OrganizationId
    department_id: DepartmentId
    unit_id: UnitId

    unit_code: str
    unit_name: str
    unit_type: UnitType = UnitType.INPATIENT
    status: UnitStatus = UnitStatus.ACTIVE

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        organization_id: OrganizationId,
        department_id: DepartmentId,
        unit_code: str,
        unit_name: str,
        unit_type: UnitType = UnitType.INPATIENT,
    ) -> Unit:
        unit_id = UnitId.generate()
        unit = cls(
            id=unit_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            department_id=department_id,
            unit_id=unit_id,
            unit_code=unit_code,
            unit_name=unit_name,
            unit_type=unit_type,
        )
        unit._mark_created()
        return unit
