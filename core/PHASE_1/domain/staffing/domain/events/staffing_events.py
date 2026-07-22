"""Staffing domain events."""

from __future__ import annotations

from dataclasses import dataclass

from core.PHASE_1.infrastructure.shared.events import DomainEvent


@dataclass(frozen=True)
class StaffRegistered(DomainEvent):
    tenant_id: str
    staff_id: str
    employee_id: str
    staff_type: str


@dataclass(frozen=True)
class StaffTerminated(DomainEvent):
    tenant_id: str
    staff_id: str


@dataclass(frozen=True)
class RoleAssigned(DomainEvent):
    tenant_id: str
    staff_id: str
    role_id: str


@dataclass(frozen=True)
class TeamCreated(DomainEvent):
    tenant_id: str
    team_id: str
    team_name: str
    team_type: str


@dataclass(frozen=True)
class ShiftScheduled(DomainEvent):
    tenant_id: str
    shift_id: str
    staff_id: str
    shift_type: str
    start_time: str


@dataclass(frozen=True)
class ShiftStarted(DomainEvent):
    tenant_id: str
    shift_id: str
    staff_id: str


@dataclass(frozen=True)
class ShiftEnded(DomainEvent):
    tenant_id: str
    shift_id: str
    staff_id: str
