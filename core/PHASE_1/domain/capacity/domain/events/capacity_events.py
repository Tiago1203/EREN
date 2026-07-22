"""Capacity domain events."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.PHASE_1.infrastructure.shared.events import DomainEvent


@dataclass(frozen=True)
class BedCreated(DomainEvent):
    """Fired when a new bed is registered."""

    tenant_id: str
    campus_id: str
    building_id: str
    floor_id: str
    room_id: str
    bed_id: str
    bed_number: str
    bed_type: str
    status: str


@dataclass(frozen=True)
class BedOccupied(DomainEvent):
    """Fired when a bed is occupied by a patient."""

    tenant_id: str
    bed_id: str
    patient_id: str
    staff_id: str | None = None


@dataclass(frozen=True)
class BedVacated(DomainEvent):
    """Fired when a patient vacates a bed."""

    tenant_id: str
    bed_id: str
    patient_id: str
    duration_hours: float | None = None


@dataclass(frozen=True)
class BedBlocked(DomainEvent):
    """Fired when a bed is temporarily blocked."""

    tenant_id: str
    bed_id: str
    reason: str = ""


@dataclass(frozen=True)
class BedUnblocked(DomainEvent):
    """Fired when a bed is unblocked."""

    tenant_id: str
    bed_id: str


@dataclass(frozen=True)
class RoomConfigured(DomainEvent):
    """Fired when a room is configured."""

    tenant_id: str
    campus_id: str
    building_id: str
    floor_id: str
    room_id: str
    room_number: str
    room_type: str


@dataclass(frozen=True)
class CampusRegistered(DomainEvent):
    """Fired when a new campus is registered."""

    tenant_id: str
    organization_id: str
    campus_id: str
    campus_code: str
    campus_name: str
