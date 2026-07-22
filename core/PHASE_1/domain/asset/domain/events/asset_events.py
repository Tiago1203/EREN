"""Asset Management domain events."""

from __future__ import annotations

from dataclasses import dataclass

from core.PHASE_1.infrastructure.shared.events import DomainEvent


@dataclass(frozen=True)
class AssetRegistered(DomainEvent):
    tenant_id: str
    asset_id: str
    asset_tag: str
    name: str


@dataclass(frozen=True)
class AssetTransferred(DomainEvent):
    tenant_id: str
    asset_id: str
    from_location_id: str | None
    to_location_id: str


@dataclass(frozen=True)
class AssetRetired(DomainEvent):
    tenant_id: str
    asset_id: str
    reason: str = ""


@dataclass(frozen=True)
class ContractSigned(DomainEvent):
    tenant_id: str
    contract_id: str
    asset_id: str
    vendor_id: str


@dataclass(frozen=True)
class WarrantyActivated(DomainEvent):
    tenant_id: str
    warranty_id: str
    asset_id: str
    expires_at: str
