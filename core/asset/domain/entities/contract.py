"""Contract entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import AggregateRoot, AssetId, ContractId, TenantId, VendorId

if TYPE_CHECKING:
    pass


class ContractType(str, Enum):
    PURCHASE = "purchase"
    SERVICE = "service"
    LEASE = "lease"
    RENTAL = "rental"
    MAINTENANCE_AGREEMENT = "maintenance_agreement"


class ContractStatus(str, Enum):
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    TERMINATED = "terminated"


@dataclass(eq=False)
class Contract(AggregateRoot):
    """Contract entity.

    Represents a contract with a vendor for an asset.
    """

    tenant_id: TenantId
    contract_id: ContractId
    asset_id: AssetId
    vendor_id: VendorId

    contract_number: str
    contract_type: ContractType

    # Dates
    start_date: date
    end_date: date

    # Financial
    total_value: Decimal = Decimal("0.00")
    payment_terms: str | None = None

    # Renewal
    auto_renew: bool = False
    renewal_terms: str | None = None

    # Status
    status: ContractStatus = ContractStatus.ACTIVE

    # Audit
    approved_at: datetime | None = None
    approved_by: str | None = None

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        asset_id: AssetId,
        vendor_id: VendorId,
        contract_number: str,
        contract_type: ContractType,
        start_date: date,
        end_date: date,
        total_value: Decimal = Decimal("0.00"),
        auto_renew: bool = False,
    ) -> Contract:
        if end_date <= start_date:
            raise ValueError("end_date must be after start_date")
        contract_id = ContractId.generate()
        contract = cls(
            id=contract_id,
            tenant_id=tenant_id,
            contract_id=contract_id,
            asset_id=asset_id,
            vendor_id=vendor_id,
            contract_number=contract_number,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            total_value=total_value,
            auto_renew=auto_renew,
        )
        contract._mark_created()
        return contract

    def renew(self, new_end_date: date) -> None:
        """Renew the contract."""
        if new_end_date <= self.end_date:
            raise ValueError("new_end_date must be after current end_date")
        self.end_date = new_end_date
        self.status = ContractStatus.ACTIVE
        self._mark_updated()

    def terminate(self) -> None:
        """Terminate the contract."""
        self.status = ContractStatus.TERMINATED
        self._mark_updated()

    def is_active(self) -> bool:
        today = date.today()
        return (
            self.status == ContractStatus.ACTIVE
            and self.start_date <= today <= self.end_date
        )
