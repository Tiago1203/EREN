"""Team entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import AggregateRoot, DepartmentId, StaffId, TeamId, TenantId

if TYPE_CHECKING:
    pass


class TeamType(str, Enum):
    NURSING = "nursing"
    BIOMEDICAL = "biomedical"
    ENGINEERING = "engineering"
    ADMINISTRATIVE = "administrative"


@dataclass(eq=False)
class Team(AggregateRoot):
    """Team entity.

    A team is a group of staff members working together.
    Teams belong to a department.
    """

    tenant_id: TenantId
    team_id: TeamId
    team_name: str
    team_type: TeamType
    department_id: DepartmentId | None = None
    team_lead_staff_id: StaffId | None = None

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        team_name: str,
        team_type: TeamType,
        department_id: DepartmentId | None = None,
    ) -> Team:
        team_id = TeamId.generate()
        team = cls(
            id=team_id,
            tenant_id=tenant_id,
            team_id=team_id,
            team_name=team_name,
            team_type=team_type,
            department_id=department_id,
        )
        team._mark_created()
        return team

    def set_lead(self, staff_id: StaffId) -> None:
        self.team_lead_staff_id = staff_id
        self._mark_updated()
