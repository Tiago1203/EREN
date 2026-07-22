"""Staff aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from enum import Enum
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import AggregateRoot, RoleId, StaffId, TeamId, TenantId

if TYPE_CHECKING:
    pass


class StaffType(str, Enum):
    PHYSICIAN = "physician"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    ENGINEER = "engineer"
    ADMIN = "admin"
    OTHER = "other"


class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


@dataclass(eq=False)
class Staff(AggregateRoot):
    """Staff aggregate root.

    Represents a hospital employee. Staff are assigned to departments,
    teams, and shifts.

    Invariants:
    1. Staff must have a valid employment status
    2. Terminated staff cannot be assigned to new shifts
    3. Email must be unique per tenant
    """

    tenant_id: TenantId
    staff_id: StaffId

    # Employment
    employee_id: str  # Hospital employee number
    first_name: str
    last_name: str
    email: str

    # Classification
    staff_type: StaffType
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    hire_date: date = field(default_factory=date.today)

    # Contact
    phone: str | None = None

    # Roles and teams
    primary_role_id: RoleId | None = None
    team_ids: list[TeamId] = field(default_factory=list)

    # Audit
    terminated_at: datetime | None = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        employee_id: str,
        first_name: str,
        last_name: str,
        email: str,
        staff_type: StaffType,
        phone: str | None = None,
        hire_date: date | None = None,
    ) -> Staff:
        staff_id = StaffId.generate()
        staff = cls(
            id=staff_id,
            tenant_id=tenant_id,
            staff_id=staff_id,
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            staff_type=staff_type,
            phone=phone,
            hire_date=hire_date or date.today(),
        )
        staff._mark_created()
        return staff

    def assign_role(self, role_id: RoleId) -> None:
        """Assign a primary role to staff."""
        self._unlock_for_mutation()
        self.primary_role_id = role_id
        self._relock_after_mutation()

    def assign_to_team(self, team_id: TeamId) -> None:
        """Assign staff to a team."""
        if team_id not in self.team_ids:
            self._unlock_for_mutation()
            self.team_ids.append(team_id)
            self._relock_after_mutation()

    def remove_from_team(self, team_id: TeamId) -> None:
        """Remove staff from a team."""
        if team_id in self.team_ids:
            self._unlock_for_mutation()
            self.team_ids.remove(team_id)
            self._relock_after_mutation()

    def terminate(self) -> None:
        """Terminate staff employment."""
        if self.employment_status == EmploymentStatus.TERMINATED:
            raise ValueError("Staff is already terminated")
        self._unlock_for_mutation()
        self.employment_status = EmploymentStatus.TERMINATED
        self.terminated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def is_active(self) -> bool:
        """Check if staff is available for assignment."""
        return self.employment_status == EmploymentStatus.ACTIVE
