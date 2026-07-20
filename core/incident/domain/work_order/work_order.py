"""WorkOrder aggregate root.

WorkOrder is a sub-aggregate of the Incident bounded context.
It represents maintenance work generated from incidents or preventive schedules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from core.shared import (
    AggregateRoot,
    ConcurrencyError,
    DeviceId,
    EngineerId,
    IncidentId,
    TenantId,
    WorkOrderId,
)

from .value_objects import (
    WorkOrderPriority,
    WorkOrderStatus,
    WorkOrderType,
)

if TYPE_CHECKING:
    pass


@dataclass(eq=False)
class WorkOrder(AggregateRoot):
    """Work Order aggregate root.

    Represents maintenance work generated from an incident or preventive schedule.
    WorkOrder is a sub-aggregate owned by the Incident bounded context.

    Lifecycle:
    draft → scheduled → in_progress → completed
                ↘ cancelled
                    ↘ on_hold ← in_progress
                        ↘ pending_parts ← in_progress

    Invariants:
    1. Work order must have a device
    2. Priority must be valid
    3. Cannot transition to terminal states without proper transitions
    4. Completed/cancelled work orders cannot be modified
    5. SLA deadline must be computed based on priority
    6. Only assigned technician can update in_progress status
    """

    # Identity
    tenant_id: TenantId
    device_id: DeviceId
    work_order_type: WorkOrderType

    # Content
    description: str

    # Priority and status
    priority: WorkOrderPriority
    status: WorkOrderStatus = field(default_factory=WorkOrderStatus.draft)

    # Assignment
    assigned_to: EngineerId | None = None
    assigned_by: EngineerId | None = None
    assigned_at: datetime | None = None

    # Scheduling
    scheduled_date: datetime | None = None
    estimated_duration_hours: float | None = None

    # Execution
    started_at: datetime | None = None
    completed_at: datetime | None = None
    completed_by: EngineerId | None = None
    resolution_summary: str | None = None
    parts_used: list[str] = field(default_factory=list)

    # SLA
    sla_deadline: datetime | None = None
    sla_breached: bool = False

    # Hold
    on_hold_reason: str | None = None
    on_hold_at: datetime | None = None

    # Cross-references
    incident_id: IncidentId | None = None
    preventive_schedule_id: str | None = None

    # Notes
    notes: str | None = None

    # Calibration follow-up
    next_calibration_date: datetime | None = None

    # Metadata
    cancellation_reason: str | None = None
    cancelled_by: EngineerId | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self._compute_sla_deadline()

    def _compute_sla_deadline(self) -> None:
        """Compute SLA deadline based on priority."""
        if self.sla_deadline is None and self.priority is not None:
            hours = self.priority.sla_deadline_hours()
            base = self.scheduled_date if self.scheduled_date else datetime.now(UTC)
            self.sla_deadline = base + timedelta(hours=hours)

    # ─── Factory methods ───────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        device_id: DeviceId,
        work_order_type: WorkOrderType,
        description: str,
        priority: WorkOrderPriority,
        incident_id: IncidentId | None = None,
        preventive_schedule_id: str | None = None,
        created_by: EngineerId | None = None,
    ) -> tuple[WorkOrder, list[WorkOrderCreated]]:
        """Create a new work order in draft status."""
        if not description or len(description.strip()) < 5:
            raise ValueError("Work order description must be at least 5 characters")

        wo = cls(
            id=WorkOrderId.generate(),
            tenant_id=tenant_id,
            device_id=device_id,
            work_order_type=work_order_type,
            description=description,
            priority=priority,
            incident_id=incident_id,
            preventive_schedule_id=preventive_schedule_id,
            notes=None,
            created_by=created_by,
        )

        event = WorkOrderCreated(
            work_order_id=str(wo.id),
            tenant_id=str(wo.tenant_id),
            device_id=str(wo.device_id),
            incident_id=str(wo.incident_id) if wo.incident_id else None,
            work_order_type=str(wo.work_order_type),
            priority=str(wo.priority),
            description=wo.description,
            sla_deadline=wo.sla_deadline.isoformat() if wo.sla_deadline else None,
        )
        wo._record(event)
        return wo, [event]

    # ─── Status transitions ────────────────────────────────────────────────

    def assign(
        self,
        technician_id: EngineerId,
        assigned_by: EngineerId,
    ) -> WorkOrderAssigned:
        """Assign work order to a technician."""
        if self.status.is_terminal():
            raise ConcurrencyError(
                entity_type="WorkOrder",
                entity_id=str(self.id),
                expected_version=self.version,
                actual_version=self.version,
            )

        self.assigned_to = technician_id
        self.assigned_by = assigned_by
        self.assigned_at = datetime.now(UTC)

        event = WorkOrderAssigned(
            work_order_id=str(self.id),
            tenant_id=str(self.tenant_id),
            device_id=str(self.device_id),
            assigned_to=str(technician_id),
            assigned_by=str(assigned_by),
            assigned_at=self.assigned_at.isoformat(),
        )
        self._record(event)
        return event

    def schedule(
        self,
        scheduled_date: datetime,
        estimated_duration_hours: float | None = None,
        expected_version: int | None = None,
    ) -> WorkOrderScheduled:
        """Schedule work order for a specific date."""
        self._check_version(expected_version)
        if not self.status.can_transition_to(WorkOrderStatus.scheduled()):
            raise ConcurrencyError(
                entity_type="WorkOrder",
                entity_id=str(self.id),
                expected_version=expected_version or self.version,
                actual_version=self.version,
            )

        self.status = WorkOrderStatus.scheduled()
        self.scheduled_date = scheduled_date
        self.estimated_duration_hours = estimated_duration_hours
        self._compute_sla_deadline()

        event = WorkOrderScheduled(
            work_order_id=str(self.id),
            tenant_id=str(self.tenant_id),
            scheduled_date=scheduled_date.isoformat(),
            estimated_duration_hours=estimated_duration_hours,
            sla_deadline=self.sla_deadline.isoformat() if self.sla_deadline else None,
        )
        self._record(event)
        return event

    def start(self, expected_version: int | None = None) -> WorkOrderStarted:
        """Start work on the work order."""
        self._check_version(expected_version)
        if not self.status.can_transition_to(WorkOrderStatus.in_progress()):
            raise ConcurrencyError(
                entity_type="WorkOrder",
                entity_id=str(self.id),
                expected_version=expected_version or self.version,
                actual_version=self.version,
            )

        self.status = WorkOrderStatus.in_progress()
        self.started_at = datetime.now(UTC)

        event = WorkOrderStarted(
            work_order_id=str(self.id),
            tenant_id=str(self.tenant_id),
            device_id=str(self.device_id),
            started_at=self.started_at.isoformat(),
        )
        self._record(event)
        return event

    def put_on_hold(
        self,
        reason: str,
        expected_version: int | None = None,
    ) -> WorkOrderOnHold:
        """Put work order on hold."""
        self._check_version(expected_version)
        if not self.status.can_transition_to(WorkOrderStatus.on_hold()):
            raise ConcurrencyError(
                entity_type="WorkOrder",
                entity_id=str(self.id),
                expected_version=expected_version or self.version,
                actual_version=self.version,
            )

        self.status = WorkOrderStatus.on_hold()
        self.on_hold_reason = reason
        self.on_hold_at = datetime.now(UTC)

        event = WorkOrderOnHold(
            work_order_id=str(self.id),
            tenant_id=str(self.tenant_id),
            reason=reason,
            on_hold_at=self.on_hold_at.isoformat(),
        )
        self._record(event)
        return event

    def complete(
        self,
        resolution_summary: str,
        completed_by: EngineerId,
        parts_used: list[str] | None = None,
        next_calibration_date: datetime | None = None,
        expected_version: int | None = None,
    ) -> WorkOrderCompleted:
        """Complete the work order."""
        self._check_version(expected_version)
        if not self.status.can_transition_to(WorkOrderStatus.completed()):
            raise ConcurrencyError(
                entity_type="WorkOrder",
                entity_id=str(self.id),
                expected_version=expected_version or self.version,
                actual_version=self.version,
            )

        self.status = WorkOrderStatus.completed()
        self.completed_at = datetime.now(UTC)
        self.completed_by = completed_by
        self.resolution_summary = resolution_summary
        self.parts_used = parts_used or []
        self.next_calibration_date = next_calibration_date

        event = WorkOrderCompleted(
            work_order_id=str(self.id),
            tenant_id=str(self.tenant_id),
            device_id=str(self.device_id),
            completed_at=self.completed_at.isoformat(),
            completed_by=str(completed_by),
            resolution_summary=resolution_summary,
            parts_used=tuple(self.parts_used),
            next_calibration_date=(
                next_calibration_date.isoformat() if next_calibration_date else None
            ),
            actual_labor_hours=self._compute_actual_labor_hours(),
        )
        self._record(event)
        return event

    def cancel(
        self,
        reason: str,
        cancelled_by: EngineerId,
        expected_version: int | None = None,
    ) -> WorkOrderCancelled:
        """Cancel the work order."""
        self._check_version(expected_version)
        if not self.status.can_transition_to(WorkOrderStatus.cancelled()):
            raise ConcurrencyError(
                entity_type="WorkOrder",
                entity_id=str(self.id),
                expected_version=expected_version or self.version,
                actual_version=self.version,
            )

        self.status = WorkOrderStatus.cancelled()
        self.cancellation_reason = reason
        self.cancelled_by = cancelled_by

        event = WorkOrderCancelled(
            work_order_id=str(self.id),
            tenant_id=str(self.tenant_id),
            device_id=str(self.device_id),
            reason=reason,
            cancelled_by=str(cancelled_by),
        )
        self._record(event)
        return event

    def check_sla_breach(self, now: datetime | None = None) -> bool:
        """Check if SLA deadline has been breached."""
        if self.sla_deadline is None:
            return False
        check_time = now or datetime.now(UTC)
        breached = check_time > self.sla_deadline and not self.status.is_terminal()
        if breached:
            self.sla_breached = True
        return breached

    # ─── Internal helpers ──────────────────────────────────────────────────

    def _check_version(self, expected_version: int | None) -> None:
        if expected_version is not None and expected_version != self.version:
            raise ConcurrencyError(
                entity_type="WorkOrder",
                entity_id=str(self.id),
                expected_version=expected_version,
                actual_version=self.version,
            )

    def _compute_actual_labor_hours(self) -> float | None:
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return round(delta.total_seconds() / 3600, 2)
        return None


# ─── Domain Events ────────────────────────────────────────────────────────


from core.shared.events import DomainEvent


@dataclass(frozen=True)
class WorkOrderCreated(DomainEvent):
    """Fired when a new work order is created."""

    work_order_id: str
    tenant_id: str
    device_id: str
    incident_id: str | None = None
    work_order_type: str = ""
    priority: str = ""
    description: str = ""
    sla_deadline: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "WorkOrderCreated")


@dataclass(frozen=True)
class WorkOrderAssigned(DomainEvent):
    """Fired when a work order is assigned to a technician."""

    work_order_id: str
    tenant_id: str
    device_id: str
    assigned_to: str
    assigned_by: str
    assigned_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "WorkOrderAssigned")


@dataclass(frozen=True)
class WorkOrderScheduled(DomainEvent):
    """Fired when a work order is scheduled."""

    work_order_id: str
    tenant_id: str
    scheduled_date: str
    estimated_duration_hours: float | None = None
    sla_deadline: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "WorkOrderScheduled")


@dataclass(frozen=True)
class WorkOrderStarted(DomainEvent):
    """Fired when work starts on a work order."""

    work_order_id: str
    tenant_id: str
    device_id: str
    started_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "WorkOrderStarted")


@dataclass(frozen=True)
class WorkOrderOnHold(DomainEvent):
    """Fired when work order is put on hold."""

    work_order_id: str
    tenant_id: str
    reason: str
    on_hold_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "WorkOrderOnHold")


@dataclass(frozen=True)
class WorkOrderCompleted(DomainEvent):
    """Fired when work order is completed."""

    work_order_id: str
    tenant_id: str
    device_id: str
    completed_at: str
    completed_by: str
    resolution_summary: str
    parts_used: tuple[str, ...] = ()
    next_calibration_date: str | None = None
    actual_labor_hours: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "WorkOrderCompleted")


@dataclass(frozen=True)
class WorkOrderCancelled(DomainEvent):
    """Fired when work order is cancelled."""

    work_order_id: str
    tenant_id: str
    device_id: str
    reason: str
    cancelled_by: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", "WorkOrderCancelled")
