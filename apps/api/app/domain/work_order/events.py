"""Work Order domain events.

Published via Transactional Outbox when significant business events occur.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class WorkOrderEvent:
    """Base class for Work Order domain events."""

    work_order_id: str
    tenant_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    caused_by: str | None = None

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class WorkOrderCreated(WorkOrderEvent):
    """Fired when a new work order is created (draft or directly scheduled)."""

    device_id: str = ""
    device_name: str = ""
    device_serial: str = ""
    work_order_type: str = ""  # corrective | preventive
    description: str = ""
    priority: str = "medium"  # low | medium | high | urgent | emergency
    incident_id: str | None = None
    preventive_schedule_id: str | None = None


@dataclass(frozen=True)
class WorkOrderAssigned(WorkOrderEvent):
    """Fired when a work order is assigned to a technician."""

    assigned_to: str = ""
    assigned_by: str = ""
    previous_assignee: str | None = None


@dataclass(frozen=True)
class WorkOrderScheduled(WorkOrderEvent):
    """Fired when a work order is scheduled for a specific date."""

    scheduled_date: str = ""
    estimated_duration_hours: int | None = None
    scheduled_by: str = ""


@dataclass(frozen=True)
class WorkOrderStarted(WorkOrderEvent):
    """Fired when work begins on a work order."""

    started_at: str = ""
    started_by: str = ""
    previous_status: str = ""


@dataclass(frozen=True)
class WorkOrderStatusChanged(WorkOrderEvent):
    """Fired when work order status changes (generic)."""

    previous_status: str = ""
    new_status: str = ""


@dataclass(frozen=True)
class WorkOrderCompleted(WorkOrderEvent):
    """Fired when work order is completed."""

    completed_at: str = ""
    completed_by: str = ""
    resolution_summary: str = ""
    parts_used: list[str] = field(default_factory=list)
    labor_hours: float | None = None
    previous_status: str = ""


@dataclass(frozen=True)
class WorkOrderCancelled(WorkOrderEvent):
    """Fired when a work order is cancelled."""

    cancelled_by: str = ""
    cancellation_reason: str = ""
    previous_status: str = ""


@dataclass(frozen=True)
class WorkOrderOnHold(WorkOrderEvent):
    """Fired when a work order is put on hold."""

    hold_reason: str = ""
    previous_status: str = ""
    resumed_by: str | None = None


@dataclass(frozen=True)
class WorkOrderUpdated(WorkOrderEvent):
    """Fired when work order fields are updated."""

    changes: dict = field(default_factory=dict)
    version: int = 1
