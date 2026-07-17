"""Organization domain events."""

from __future__ import annotations

from dataclasses import dataclass

from core.shared.events import DomainEvent


@dataclass(frozen=True)
class OrganizationRegistered(DomainEvent):
    tenant_id: str
    organization_id: str
    legal_name: str


@dataclass(frozen=True)
class HospitalRegistered(DomainEvent):
    tenant_id: str
    organization_id: str
    hospital_id: str
    hospital_code: str
    hospital_name: str
    hospital_type: str


@dataclass(frozen=True)
class CampusRegistered(DomainEvent):
    tenant_id: str
    organization_id: str
    campus_id: str
    campus_code: str
    campus_name: str


@dataclass(frozen=True)
class BuildingRegistered(DomainEvent):
    tenant_id: str
    campus_id: str
    building_id: str
    building_code: str
