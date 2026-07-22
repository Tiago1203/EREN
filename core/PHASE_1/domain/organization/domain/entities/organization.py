"""Organization aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from enum import Enum
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import AggregateRoot, OrganizationId, TenantId

if TYPE_CHECKING:
    pass


class OwnershipType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    NON_PROFIT = "non_profit"
    GOVERNMENT = "government"


class OrganizationStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISSOLVED = "dissolved"


@dataclass(eq=False)
class Organization(AggregateRoot):
    """Organization aggregate root.

    The organization is the top-level legal entity in EREN.
    One tenant = one organization (enforced by multi-tenancy).

    Invariants:
    1. An Organization must have a valid status
    2. tax_id must be unique per tenant
    """

    tenant_id: TenantId
    organization_id: OrganizationId

    # Legal
    legal_name: str
    doing_business_as: str | None = None
    tax_id: str | None = None

    # Classification
    ownership_type: OwnershipType = OwnershipType.PRIVATE

    # Dates
    founded_date: date | None = None

    # Status
    status: OrganizationStatus = OrganizationStatus.ACTIVE

    # Audit

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        legal_name: str,
        ownership_type: OwnershipType = OwnershipType.PRIVATE,
        doing_business_as: str | None = None,
        tax_id: str | None = None,
        founded_date: date | None = None,
    ) -> Organization:
        org_id = OrganizationId.generate()
        org = cls(
            id=org_id,
            tenant_id=tenant_id,
            organization_id=org_id,
            legal_name=legal_name,
            ownership_type=ownership_type,
            doing_business_as=doing_business_as,
            tax_id=tax_id,
            founded_date=founded_date,
        )
        org._mark_created()
        return org

    def suspend(self) -> None:
        """Suspend the organization."""
        if self.status == OrganizationStatus.DISSOLVED:
            raise ValueError("Cannot suspend a dissolved organization")
        self.status = OrganizationStatus.SUSPENDED
        self._mark_updated()

    def activate(self) -> None:
        """Reactivate the organization."""
        self.status = OrganizationStatus.ACTIVE
        self._mark_updated()
