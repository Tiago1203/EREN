"""Hospital aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from enum import Enum
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import AggregateRoot, HospitalId, OrganizationId, TenantId

if TYPE_CHECKING:
    pass


class HospitalType(str, Enum):
    ACADEMIC = "academic"
    COMMUNITY = "community"
    SPECIALTY = "specialty"
    TRAUMA_CENTER = "trauma_center"


class AccreditationStatus(str, Enum):
    ACCREDITED = "accredited"
    PENDING = "pending"
    EXPIRED = "expired"


@dataclass(eq=False)
class Hospital(AggregateRoot):
    """Hospital aggregate root.

    Represents a hospital facility within an organization.
    Each hospital belongs to exactly one organization.

    Invariants:
    1. Hospital must belong to exactly one Organization
    2. license_expiry_date must be in the future if accredited
    """

    tenant_id: TenantId
    organization_id: OrganizationId
    hospital_id: HospitalId

    # Identification
    hospital_code: str  # e.g., "HH-NYC-01"
    hospital_name: str

    # Classification
    hospital_type: HospitalType

    # Licensing
    license_number: str | None = None
    accreditation_status: AccreditationStatus = AccreditationStatus.PENDING
    license_expiry_date: date | None = None

    # Contact
    contact_email: str | None = None
    contact_phone: str | None = None

    # Audit

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        organization_id: OrganizationId,
        hospital_code: str,
        hospital_name: str,
        hospital_type: HospitalType,
        license_number: str | None = None,
        contact_email: str | None = None,
        contact_phone: str | None = None,
    ) -> Hospital:
        hospital_id = HospitalId.generate()
        hospital = cls(
            id=hospital_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            hospital_id=hospital_id,
            hospital_code=hospital_code,
            hospital_name=hospital_name,
            hospital_type=hospital_type,
            license_number=license_number,
            contact_email=contact_email,
            contact_phone=contact_phone,
        )
        hospital._mark_created()
        return hospital

    def update_accreditation(
        self,
        status: AccreditationStatus,
        expiry_date: date | None = None,
    ) -> None:
        """Update accreditation status."""
        self.accreditation_status = status
        if expiry_date:
            self.license_expiry_date = expiry_date
        self._mark_updated()
