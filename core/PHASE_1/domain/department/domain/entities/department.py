"""Department aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import AggregateRoot, DepartmentGroupId, DepartmentId, OrganizationId, StaffId, TenantId

if TYPE_CHECKING:
    pass


class DepartmentType(str, Enum):
    CLINICAL = "clinical"
    DIAGNOSTIC = "diagnostic"
    SUPPORT = "support"
    ADMINISTRATIVE = "administrative"


class DepartmentStatus(str, Enum):
    ACTIVE = "active"
    RESTRUCTURED = "restructured"
    CLOSED = "closed"


@dataclass(eq=False)
class Department(AggregateRoot):
    """Department aggregate root.

    Represents a hospital department (ICU, Emergency, Radiology, etc.).
    Departments belong to an organization and may have a parent department.

    Invariants:
    1. Department must belong to exactly one Organization
    2. Hierarchy depth ≤ 3 levels
    3. Cost center must be unique per organization
    """

    tenant_id: TenantId
    organization_id: OrganizationId
    department_id: DepartmentId

    # Identification
    department_code: str  # e.g., "ICU-01", "RAD-02"
    department_name: str

    # Hierarchy
    department_type: DepartmentType
    parent_department_id: DepartmentId | None = None
    department_group_id: DepartmentGroupId | None = None

    # Financial
    cost_center: str | None = None
    budget_allocated: Decimal | None = None

    # Management
    head_staff_id: StaffId | None = None

    # Status
    status: DepartmentStatus = DepartmentStatus.ACTIVE

    # Audit

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        organization_id: OrganizationId,
        department_code: str,
        department_name: str,
        department_type: DepartmentType,
        parent_department_id: DepartmentId | None = None,
        department_group_id: DepartmentGroupId | None = None,
        cost_center: str | None = None,
        budget_allocated: Decimal | None = None,
    ) -> Department:
        dept_id = DepartmentId.generate()
        dept = cls(
            id=dept_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            department_id=dept_id,
            department_code=department_code,
            department_name=department_name,
            department_type=department_type,
            parent_department_id=parent_department_id,
            department_group_id=department_group_id,
            cost_center=cost_center,
            budget_allocated=budget_allocated,
        )
        dept._mark_created()
        return dept

    def set_head(self, staff_id: StaffId) -> None:
        self.head_staff_id = staff_id
        self._mark_updated()

    def close(self) -> None:
        self.status = DepartmentStatus.CLOSED
        self._mark_updated()
