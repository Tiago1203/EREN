"""Work Order application service.

Orchestrates domain operations, persistence, and event publishing for work orders.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from app.domain.work_order.events import (
    WorkOrderAssigned,
    WorkOrderCancelled,
    WorkOrderCompleted,
    WorkOrderCreated,
    WorkOrderEvent,
    WorkOrderOnHold,
    WorkOrderScheduled,
    WorkOrderStarted,
    WorkOrderStatusChanged,
    WorkOrderUpdated,
)
from app.domain.work_order.repository import WorkOrderRepository

if TYPE_CHECKING:
    from app.infrastructure.messaging.outbox import TransactionalOutbox
    from app.infrastructure.models.work_order import WorkOrderModel

logger = logging.getLogger(__name__)


VALID_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"scheduled", "cancelled"},
    "scheduled": {"in_progress", "cancelled", "on_hold"},
    "in_progress": {"pending_parts", "completed", "cancelled", "on_hold"},
    "pending_parts": {"in_progress", "cancelled", "on_hold"},
    "on_hold": {"scheduled", "in_progress", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}

SLA_HOURS_BY_PRIORITY: dict[str, int] = {
    "low": 720,       # 30 days
    "medium": 168,    # 7 days
    "high": 72,       # 3 days
    "urgent": 24,     # 1 day
    "emergency": 4,   # 4 hours
}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _compute_sla_deadline(priority: str, scheduled_date: datetime | None = None) -> datetime:
    hours = SLA_HOURS_BY_PRIORITY.get(priority, 168)
    base = scheduled_date if scheduled_date else _utcnow()
    return base + timedelta(hours=hours)


@dataclass
class WorkOrderService:
    """Application service for Work Order lifecycle operations.

    Coordinates:
    1. Domain model mutations
    2. Persistence (via repository)
    3. Event publishing (via TransactionalOutbox)
    4. Business validations (status transitions, SLA)
    """

    repository: WorkOrderRepository
    outbox: TransactionalOutbox

    # ─── Create Work Order ────────────────────────────────────────────────────

    async def create_work_order(
        self,
        *,
        tenant_id: str,
        device_id: str,
        device_name: str,
        device_serial: str,
        work_order_type: str,
        description: str,
        priority: str = "medium",
        incident_id: str | None = None,
        preventive_schedule_id: str | None = None,
        created_by: str | None = None,
        correlation_id: str | None = None,
    ) -> WorkOrderModel:
        """Create a new work order in draft status.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        if not device_id:
            raise ValueError("device_id is required")
        if not description or not description.strip():
            raise ValueError("description is required")
        if work_order_type not in ("corrective", "preventive"):
            raise ValueError(f"work_order_type must be 'corrective' or 'preventive', got '{work_order_type}'")
        if priority not in SLA_HOURS_BY_PRIORITY:
            raise ValueError(f"priority must be one of: {list(SLA_HOURS_BY_PRIORITY.keys())}")

        work_order_id = str(uuid.uuid4())

        work_order = await self.repository.save(
            tenant_id=tenant_id,
            work_order_id=work_order_id,
            device_id=device_id,
            work_order_type=work_order_type,
            description=description.strip(),
            priority=priority,
            status="draft",
            created_by=created_by,
            incident_id=incident_id,
            preventive_schedule_id=preventive_schedule_id,
        )

        event = WorkOrderCreated(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            device_id=device_id,
            device_name=device_name,
            device_serial=device_serial,
            work_order_type=work_order_type,
            description=description.strip(),
            priority=priority,
            incident_id=incident_id,
            preventive_schedule_id=preventive_schedule_id,
            correlation_id=correlation_id,
            caused_by=created_by,
        )
        self._publish_event(event)

        logger.info(
            "Work order created",
            extra={
                "work_order_id": work_order_id,
                "tenant_id": tenant_id,
                "device_id": device_id,
                "priority": priority,
                "correlation_id": correlation_id,
            },
        )
        return work_order

    # ─── Schedule Work Order ─────────────────────────────────────────────────

    async def schedule_work_order(
        self,
        *,
        work_order_id: str,
        tenant_id: str,
        scheduled_date: datetime,
        estimated_duration_hours: int | None = None,
        assigned_to: str | None = None,
        expected_version: int,
        scheduled_by: str,
        correlation_id: str | None = None,
    ) -> WorkOrderModel:
        """Schedule a draft work order for a specific date.

        Raises:
            ValueError: If work order not found, wrong status, or version mismatch.
        """
        work_order = await self.repository.get_by_id(work_order_id, tenant_id)
        if work_order is None:
            raise ValueError(f"Work order '{work_order_id}' not found.")

        if work_order.status != "draft":
            raise ValueError(
                f"Cannot schedule work order '{work_order_id}': status is '{work_order.status}', "
                f"expected 'draft'."
            )

        if work_order.version != expected_version:
            raise ValueError(
                f"Work order '{work_order_id}' version mismatch: expected {expected_version}, "
                f"found {work_order.version}."
            )

        sla_deadline = _compute_sla_deadline(work_order.priority, scheduled_date)

        updates: dict[str, Any] = {
            "status": "scheduled",
            "scheduled_date": scheduled_date,
            "estimated_duration_hours": estimated_duration_hours,
            "sla_deadline": sla_deadline,
        }
        if assigned_to:
            updates["assigned_to"] = assigned_to

        updated = await self.repository.update(work_order, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = WorkOrderScheduled(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            scheduled_date=scheduled_date.isoformat(),
            estimated_duration_hours=estimated_duration_hours,
            scheduled_by=scheduled_by,
            correlation_id=correlation_id,
            caused_by=scheduled_by,
        )
        self._publish_event(event)

        if assigned_to:
            assign_event = WorkOrderAssigned(
                work_order_id=work_order_id,
                tenant_id=tenant_id,
                assigned_to=assigned_to,
                assigned_by=scheduled_by,
                correlation_id=correlation_id,
                caused_by=scheduled_by,
            )
            self._publish_event(assign_event)

        logger.info(
            "Work order scheduled",
            extra={
                "work_order_id": work_order_id,
                "tenant_id": tenant_id,
                "scheduled_date": scheduled_date.isoformat(),
                "assigned_to": assigned_to,
            },
        )
        return updated

    # ─── Assign Technician ───────────────────────────────────────────────────

    async def assign_work_order(
        self,
        *,
        work_order_id: str,
        tenant_id: str,
        assigned_to: str,
        assigned_by: str,
        expected_version: int,
        correlation_id: str | None = None,
    ) -> WorkOrderModel:
        """Assign or reassign a work order to a technician.

        Raises:
            ValueError: If work order not found, already completed/cancelled,
                       or version mismatch.
        """
        if not assigned_to or not assigned_to.strip():
            raise ValueError("assigned_to is required")

        work_order = await self.repository.get_by_id(work_order_id, tenant_id)
        if work_order is None:
            raise ValueError(f"Work order '{work_order_id}' not found.")

        if work_order.status in ("completed", "cancelled"):
            raise ValueError(
                f"Cannot assign work order '{work_order_id}': status is '{work_order.status}'."
            )

        if work_order.version != expected_version:
            raise ValueError("Concurrent modification detected.")

        previous_assignee = work_order.assigned_to

        updated = await self.repository.update(
            work_order, expected_version, assigned_to=assigned_to.strip()
        )
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = WorkOrderAssigned(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            previous_assignee=previous_assignee,
            correlation_id=correlation_id,
            caused_by=assigned_by,
        )
        self._publish_event(event)

        logger.info(
            "Work order assigned",
            extra={
                "work_order_id": work_order_id,
                "tenant_id": tenant_id,
                "assigned_to": assigned_to,
                "previous_assignee": previous_assignee,
            },
        )
        return updated

    # ─── Start Work Order ───────────────────────────────────────────────────

    async def start_work_order(
        self,
        *,
        work_order_id: str,
        tenant_id: str,
        started_by: str,
        expected_version: int,
        correlation_id: str | None = None,
    ) -> WorkOrderModel:
        """Start work on a scheduled work order.

        Raises:
            ValueError: If work order not found, wrong status, or version mismatch.
        """
        work_order = await self.repository.get_by_id(work_order_id, tenant_id)
        if work_order is None:
            raise ValueError(f"Work order '{work_order_id}' not found.")

        if work_order.status not in ("scheduled", "on_hold"):
            raise ValueError(
                f"Cannot start work order '{work_order_id}': status is '{work_order.status}', "
                f"expected 'scheduled' or 'on_hold'."
            )

        if work_order.version != expected_version:
            raise ValueError("Concurrent modification detected.")

        previous_status = work_order.status
        started_at = _utcnow()

        # If resuming from hold, clear hold metadata
        on_hold_reason = None
        if work_order.status == "on_hold":
            on_hold_reason = work_order.on_hold_reason
            work_order.on_hold_reason = None

        updates: dict[str, Any] = {
            "status": "in_progress",
            "started_at": started_at,
        }

        updated = await self.repository.update(work_order, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = WorkOrderStarted(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            started_at=started_at.isoformat(),
            started_by=started_by,
            previous_status=previous_status,
            correlation_id=correlation_id,
            caused_by=started_by,
        )
        self._publish_event(event)

        logger.info(
            "Work order started",
            extra={
                "work_order_id": work_order_id,
                "tenant_id": tenant_id,
                "previous_status": previous_status,
            },
        )
        return updated

    # ─── Complete Work Order ────────────────────────────────────────────────

    async def complete_work_order(
        self,
        *,
        work_order_id: str,
        tenant_id: str,
        completed_by: str,
        expected_version: int,
        resolution_summary: str = "",
        parts_used: list[str] | None = None,
        labor_hours: float | None = None,
        next_calibration_date: datetime | None = None,
        correlation_id: str | None = None,
    ) -> WorkOrderModel:
        """Complete a work order.

        Raises:
            ValueError: If work order not found, wrong status, or version mismatch.
        """
        work_order = await self.repository.get_by_id(work_order_id, tenant_id)
        if work_order is None:
            raise ValueError(f"Work order '{work_order_id}' not found.")

        if work_order.status not in ("in_progress", "pending_parts", "scheduled"):
            raise ValueError(
                f"Cannot complete work order '{work_order_id}': status is '{work_order.status}', "
                f"expected 'in_progress', 'pending_parts', or 'scheduled'."
            )

        if work_order.version != expected_version:
            raise ValueError("Concurrent modification detected.")

        previous_status = work_order.status
        completed_at = _utcnow()

        updates: dict[str, Any] = {
            "status": "completed",
            "completed_at": completed_at,
            "completed_by": completed_by,
            "resolution_summary": resolution_summary,
        }
        if parts_used:
            updates["parts_used"] = parts_used
        if labor_hours is not None:
            updates["actual_labor_hours"] = labor_hours
        if next_calibration_date:
            updates["next_calibration_date"] = next_calibration_date

        updated = await self.repository.update(work_order, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = WorkOrderCompleted(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            completed_at=completed_at.isoformat(),
            completed_by=completed_by,
            resolution_summary=resolution_summary,
            parts_used=parts_used or [],
            labor_hours=labor_hours,
            previous_status=previous_status,
            correlation_id=correlation_id,
            caused_by=completed_by,
        )
        self._publish_event(event)

        logger.info(
            "Work order completed",
            extra={
                "work_order_id": work_order_id,
                "tenant_id": tenant_id,
                "completed_by": completed_by,
                "labor_hours": labor_hours,
            },
        )
        return updated

    # ─── Cancel Work Order ──────────────────────────────────────────────────

    async def cancel_work_order(
        self,
        *,
        work_order_id: str,
        tenant_id: str,
        cancelled_by: str,
        cancellation_reason: str,
        expected_version: int,
        correlation_id: str | None = None,
    ) -> WorkOrderModel:
        """Cancel a work order.

        Raises:
            ValueError: If work order not found, already completed/cancelled,
                       or version mismatch.
        """
        work_order = await self.repository.get_by_id(work_order_id, tenant_id)
        if work_order is None:
            raise ValueError(f"Work order '{work_order_id}' not found.")

        if work_order.status in ("completed", "cancelled"):
            raise ValueError(
                f"Cannot cancel work order '{work_order_id}': status is '{work_order.status}'."
            )

        if work_order.version != expected_version:
            raise ValueError("Concurrent modification detected.")

        previous_status = work_order.status

        updated = await self.repository.update(
            work_order, expected_version,
            status="cancelled",
            cancellation_reason=cancellation_reason,
            cancelled_by=cancelled_by,
        )
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = WorkOrderCancelled(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            cancelled_by=cancelled_by,
            cancellation_reason=cancellation_reason,
            previous_status=previous_status,
            correlation_id=correlation_id,
            caused_by=cancelled_by,
        )
        self._publish_event(event)

        logger.info(
            "Work order cancelled",
            extra={
                "work_order_id": work_order_id,
                "tenant_id": tenant_id,
                "cancelled_by": cancelled_by,
                "reason": cancellation_reason,
            },
        )
        return updated

    # ─── Put On Hold ───────────────────────────────────────────────────────

    async def put_on_hold(
        self,
        *,
        work_order_id: str,
        tenant_id: str,
        hold_reason: str,
        put_on_hold_by: str,
        expected_version: int,
        correlation_id: str | None = None,
    ) -> WorkOrderModel:
        """Put a work order on hold.

        Raises:
            ValueError: If work order not found, wrong status, or version mismatch.
        """
        work_order = await self.repository.get_by_id(work_order_id, tenant_id)
        if work_order is None:
            raise ValueError(f"Work order '{work_order_id}' not found.")

        if work_order.status not in ("scheduled", "in_progress", "pending_parts"):
            raise ValueError(
                f"Cannot put work order '{work_order_id}' on hold: status is '{work_order.status}'."
            )

        if work_order.version != expected_version:
            raise ValueError("Concurrent modification detected.")

        previous_status = work_order.status

        updated = await self.repository.update(
            work_order, expected_version,
            status="on_hold",
            on_hold_reason=hold_reason,
        )
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = WorkOrderOnHold(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            hold_reason=hold_reason,
            previous_status=previous_status,
            resumed_by=None,
            correlation_id=correlation_id,
            caused_by=put_on_hold_by,
        )
        self._publish_event(event)

        logger.info(
            "Work order put on hold",
            extra={
                "work_order_id": work_order_id,
                "tenant_id": tenant_id,
                "hold_reason": hold_reason,
            },
        )
        return updated

    # ─── Update Work Order ───────────────────────────────────────────────────

    async def update_work_order(
        self,
        *,
        work_order_id: str,
        tenant_id: str,
        expected_version: int,
        updated_by: str | None = None,
        correlation_id: str | None = None,
        **fields: Any,
    ) -> WorkOrderModel | None:
        """Update work order fields with optimistic locking.

        Only certain fields can be updated depending on status.
        """
        work_order = await self.repository.get_by_id(work_order_id, tenant_id)
        if work_order is None:
            raise ValueError(f"Work order '{work_order_id}' not found.")

        if work_order.version != expected_version:
            raise ValueError("Concurrent modification detected.")

        if work_order.status in ("completed", "cancelled"):
            raise ValueError(
                f"Cannot update work order '{work_order_id}': status is '{work_order.status}'."
            )

        allowed = {
            "description",
            "priority",
            "scheduled_date",
            "estimated_duration_hours",
            "notes",
        }
        updates = {k: v for k, v in fields.items() if k in allowed and v is not None}

        if "priority" in updates and updates["priority"] not in SLA_HOURS_BY_PRIORITY:
            raise ValueError(f"priority must be one of: {list(SLA_HOURS_BY_PRIORITY.keys())}")

        if "scheduled_date" in updates:
            updates["sla_deadline"] = _compute_sla_deadline(
                updates.get("priority", work_order.priority),
                updates["scheduled_date"],
            )

        updated = await self.repository.update(work_order, expected_version, **updates)
        if updated is None:
            raise ValueError("Concurrent modification detected.")

        event = WorkOrderUpdated(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            changes=updates,
            version=expected_version + 1,
            correlation_id=correlation_id,
            caused_by=updated_by,
        )
        self._publish_event(event)

        logger.info(
            "Work order updated",
            extra={"work_order_id": work_order_id, "tenant_id": tenant_id, "changes": updates},
        )
        return updated

    # ─── Queries ───────────────────────────────────────────────────────────

    async def get_work_order(self, work_order_id: str, tenant_id: str) -> WorkOrderModel | None:
        """Get a work order by ID within tenant scope."""
        return await self.repository.get_by_id(work_order_id, tenant_id)

    async def list_work_orders(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        status: str | None = None,
        priority: str | None = None,
        assigned_to: str | None = None,
        device_id: str | None = None,
        work_order_type: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[WorkOrderModel], int]:
        """List work orders with pagination and filters."""
        return await self.repository.list_by_tenant(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
            status_filter=status,
            priority_filter=priority,
            assigned_to=assigned_to,
            device_id=device_id,
            work_order_type=work_order_type,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def list_overdue_work_orders(self, tenant_id: str) -> list[WorkOrderModel]:
        """List work orders that have breached their SLA deadline."""
        return await self.repository.list_overdue(tenant_id)

    # ─── Delete ────────────────────────────────────────────────────────────

    async def delete_work_order(self, work_order_id: str, tenant_id: str) -> bool:
        """Delete a work order (only allowed in draft or cancelled status)."""
        work_order = await self.repository.get_by_id(work_order_id, tenant_id)
        if work_order is None:
            return False
        if work_order.status not in ("draft", "cancelled"):
            raise ValueError(
                f"Cannot delete work order '{work_order_id}': status is '{work_order.status}'. "
                f"Only 'draft' or 'cancelled' work orders can be deleted."
            )

        logger.info(
            "Work order deleted",
            extra={"work_order_id": work_order_id, "tenant_id": tenant_id},
        )
        return await self.repository.delete(work_order_id, tenant_id)

    # ─── Internal ────────────────────────────────────────────────────────────

    def _publish_event(self, event: WorkOrderEvent) -> None:
        """Publish a domain event to the transactional outbox."""
        self.outbox.append(
            event_type=event.event_type,
            payload={
                "work_order_id": event.work_order_id,
                "tenant_id": event.tenant_id,
                "event_type": event.event_type,
                "occurred_at": event.occurred_at.isoformat(),
                "correlation_id": event.correlation_id,
                "caused_by": event.caused_by,
                **{f.name: getattr(event, f.name) for f in event.__dataclass_fields__.values()},
            },
            aggregate_type="WorkOrder",
            correlation_id=event.correlation_id,
        )
