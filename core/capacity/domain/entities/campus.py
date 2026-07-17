"""Campus entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import AggregateRoot, CampusId, OrganizationId, TenantId

if TYPE_CHECKING:
    pass


class CampusStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PLANNING = "planning"


@dataclass(eq=False)
class Campus(AggregateRoot):
    """Campus aggregate root.

    A campus is a geographic cluster of buildings within an organization.
    Each campus belongs to exactly one organization.

    Invariants:
    1. Campus must belong to exactly one Organization
    2. Campus must have a valid status
    """

    # Identity
    tenant_id: TenantId
    organization_id: OrganizationId
    campus_id: CampusId

    # Core attributes
    campus_code: str
    campus_name: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    timezone: str  # IANA timezone

    # Metadata
    status: CampusStatus = CampusStatus.ACTIVE

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        organization_id: OrganizationId,
        campus_code: str,
        campus_name: str,
        address: str,
        city: str,
        state: str,
        country: str,
        postal_code: str,
        timezone: str,
    ) -> Campus:
        """Create a new campus."""
        campus_id = CampusId.generate()
        campus = cls(
            id=campus_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            campus_id=campus_id,
            campus_code=campus_code,
            campus_name=campus_name,
            address=address,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            timezone=timezone,
        )
        campus._mark_created()
        return campus

    def activate(self) -> None:
        """Activate campus."""
        if self.status == CampusStatus.INACTIVE:
            self._unlock_for_mutation()
            self.status = CampusStatus.ACTIVE
            self._relock_after_mutation()

    def deactivate(self) -> None:
        """Deactivate campus."""
        if self.status != CampusStatus.PLANNING:
            self._unlock_for_mutation()
            self.status = CampusStatus.INACTIVE
            self._relock_after_mutation()
