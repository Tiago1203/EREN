"""Manufacturer entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from core.PHASE_1.infrastructure.shared import AggregateRoot, ManufacturerId, TenantId

if TYPE_CHECKING:
    pass


@dataclass(eq=False)
class Manufacturer(AggregateRoot):
    """Manufacturer entity.

    Represents a medical device manufacturer.
    """

    tenant_id: TenantId
    manufacturer_id: ManufacturerId
    manufacturer_name: str
    manufacturer_code: str
    country_of_origin: str | None = None
    website: str | None = None
    support_email: str | None = None

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        manufacturer_name: str,
        manufacturer_code: str,
        country_of_origin: str | None = None,
        website: str | None = None,
    ) -> Manufacturer:
        mfr_id = ManufacturerId.generate()
        mfr = cls(
            id=mfr_id,
            tenant_id=tenant_id,
            manufacturer_id=mfr_id,
            manufacturer_name=manufacturer_name,
            manufacturer_code=manufacturer_code,
            country_of_origin=country_of_origin,
            website=website,
        )
        mfr._mark_created()
        return mfr
