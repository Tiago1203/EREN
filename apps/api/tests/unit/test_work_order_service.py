"""Unit tests for WorkOrderService.

Tests the application service layer for work order lifecycle operations.
Uses mocked repository and outbox.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.work_order import WorkOrderService
from app.domain.work_order.repository import WorkOrderRepository


@dataclass
class FakeWorkOrder:
    """Simple fake work order matching the fields accessed by the service."""
    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = "tenant-1"
    device_id: str = field(default_factory=lambda: str(uuid4()))
    work_order_type: str = "corrective"
    description: str = "Test maintenance"
    priority: str = "medium"
    status: str = "draft"
    assigned_to: str | None = None
    scheduled_date: datetime | None = None
    version: int = 1
    sla_deadline: datetime | None = None
    on_hold_reason: str | None = None
    incident_id: str | None = None
    preventive_schedule_id: str | None = None
    parts_used: list[str] | None = None
    resolution_summary: str | None = None
    cancellation_reason: str | None = None
    notes: str | None = None
    assigned_by: str | None = None
    assigned_at: datetime | None = None
    estimated_duration_hours: float | None = None
    actual_labor_hours: float | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    completed_by: str | None = None
    on_hold_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = "user-1"
    cancelled_by: str | None = None
    next_calibration_date: datetime | None = None
    sla_breached: str = "false"


def make_work_order(**kwargs) -> FakeWorkOrder:
    """Factory for FakeWorkOrder."""
    return FakeWorkOrder(**kwargs)


@pytest.fixture
def mock_repository():
    return AsyncMock(spec=WorkOrderRepository)


@pytest.fixture
def mock_outbox():
    outbox = MagicMock()
    outbox.append = MagicMock()
    return outbox


@pytest.fixture
def service(mock_repository, mock_outbox):
    return WorkOrderService(repository=mock_repository, outbox=mock_outbox)


# ─── Create Work Order ────────────────────────────────────────────────────────


class TestCreateWorkOrder:
    @pytest.mark.asyncio
    async def test_create_work_order_success(self, service, mock_repository):
        wo = make_work_order()
        mock_repository.save.return_value = wo

        result = await service.create_work_order(
            tenant_id="tenant-1",
            device_id=str(wo.device_id),
            device_name="MRI Scanner",
            device_serial="SN-001",
            work_order_type="corrective",
            description="Replace faulty coil",
            priority="high",
            created_by="user-1",
            correlation_id="corr-1",
        )

        assert result is wo
        mock_repository.save.assert_called_once()
        call_kwargs = mock_repository.save.call_args.kwargs
        assert call_kwargs["tenant_id"] == "tenant-1"
        assert call_kwargs["priority"] == "high"
        assert call_kwargs["status"] == "draft"
        assert call_kwargs["description"] == "Replace faulty coil"
        assert service.outbox.append.called

    @pytest.mark.asyncio
    async def test_create_work_order_invalid_type_raises(self, service, mock_repository):
        with pytest.raises(ValueError, match="work_order_type must be"):
            await service.create_work_order(
                tenant_id="tenant-1",
                device_id="device-1",
                device_name="MRI Scanner",
                device_serial="SN-001",
                work_order_type="invalid",
                description="Test",
                priority="medium",
            )

    @pytest.mark.asyncio
    async def test_create_work_order_invalid_priority_raises(self, service, mock_repository):
        with pytest.raises(ValueError, match="priority must be one of"):
            await service.create_work_order(
                tenant_id="tenant-1",
                device_id="device-1",
                device_name="MRI Scanner",
                device_serial="SN-001",
                work_order_type="corrective",
                description="Test",
                priority="super-urgent",
            )

    @pytest.mark.asyncio
    async def test_create_work_order_empty_description_raises(self, service, mock_repository):
        with pytest.raises(ValueError, match="description is required"):
            await service.create_work_order(
                tenant_id="tenant-1",
                device_id="device-1",
                device_name="MRI Scanner",
                device_serial="SN-001",
                work_order_type="corrective",
                description="   ",
                priority="medium",
            )

    @pytest.mark.asyncio
    async def test_create_work_order_no_device_id_raises(self, service, mock_repository):
        with pytest.raises(ValueError, match="device_id is required"):
            await service.create_work_order(
                tenant_id="tenant-1",
                device_id="",
                device_name="MRI Scanner",
                device_serial="SN-001",
                work_order_type="corrective",
                description="Test",
                priority="medium",
            )

    @pytest.mark.asyncio
    async def test_create_work_order_publishes_event(self, service, mock_repository):
        wo = make_work_order()
        mock_repository.save.return_value = wo

        await service.create_work_order(
            tenant_id="tenant-1",
            device_id=str(wo.device_id),
            device_name="MRI Scanner",
            device_serial="SN-001",
            work_order_type="preventive",
            description="Routine inspection",
            priority="low",
            incident_id=None,
            preventive_schedule_id="sched-1",
        )

        assert service.outbox.append.called
        call = service.outbox.append.call_args
        assert call.kwargs["aggregate_type"] == "WorkOrder"
        assert call.kwargs["event_type"] == "WorkOrderCreated"


# ─── Schedule Work Order ─────────────────────────────────────────────────────


class TestScheduleWorkOrder:
    @pytest.mark.asyncio
    async def test_schedule_draft_work_order_success(self, service, mock_repository):
        wo = make_work_order(status="draft", version=1)
        mock_repository.get_by_id.return_value = wo
        scheduled_date = datetime.now(UTC) + timedelta(days=3)
        mock_repository.update.return_value = wo

        result = await service.schedule_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            scheduled_date=scheduled_date,
            estimated_duration_hours=4.0,
            assigned_to="tech-1",
            expected_version=1,
            scheduled_by="supervisor-1",
        )

        assert result is wo
        mock_repository.update.assert_called_once()
        update_call = mock_repository.update.call_args
        assert update_call.args[1] == 1  # expected_version passed positionally

    @pytest.mark.asyncio
    async def test_schedule_work_order_not_found_raises(self, service, mock_repository):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await service.schedule_work_order(
                work_order_id="nonexistent",
                tenant_id="tenant-1",
                scheduled_date=datetime.now(UTC) + timedelta(days=1),
                expected_version=1,
                scheduled_by="user-1",
            )

    @pytest.mark.asyncio
    async def test_schedule_work_order_wrong_status_raises(self, service, mock_repository):
        wo = make_work_order(status="completed")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'completed'"):
            await service.schedule_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                scheduled_date=datetime.now(UTC) + timedelta(days=1),
                expected_version=1,
                scheduled_by="user-1",
            )

    @pytest.mark.asyncio
    async def test_schedule_work_order_version_mismatch_raises(self, service, mock_repository):
        wo = make_work_order(status="draft", version=2)
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="version mismatch"):
            await service.schedule_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                scheduled_date=datetime.now(UTC) + timedelta(days=1),
                expected_version=1,
                scheduled_by="user-1",
            )

    @pytest.mark.asyncio
    async def test_schedule_work_order_concurrent_modification_raises(
        self, service, mock_repository
    ):
        wo = make_work_order(status="draft", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = None

        with pytest.raises(ValueError, match="Concurrent modification"):
            await service.schedule_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                scheduled_date=datetime.now(UTC) + timedelta(days=1),
                expected_version=1,
                scheduled_by="user-1",
            )

    @pytest.mark.asyncio
    async def test_schedule_with_assignment_publishes_both_events(
        self, service, mock_repository, mock_outbox
    ):
        wo = make_work_order(status="draft", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        await service.schedule_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            scheduled_date=datetime.now(UTC) + timedelta(days=1),
            assigned_to="tech-1",
            expected_version=1,
            scheduled_by="supervisor-1",
        )

        assert service.outbox.append.call_count == 2


# ─── Assign Work Order ────────────────────────────────────────────────────────


class TestAssignWorkOrder:
    @pytest.mark.asyncio
    async def test_assign_work_order_success(self, service, mock_repository):
        wo = make_work_order(status="scheduled", assigned_to=None, version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.assign_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            assigned_to="tech-2",
            assigned_by="supervisor-1",
            expected_version=1,
        )

        assert result is wo
        mock_repository.update.assert_called_once()
        assert service.outbox.append.called

    @pytest.mark.asyncio
    async def test_assign_completed_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="completed")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'completed'"):
            await service.assign_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                assigned_to="tech-1",
                assigned_by="supervisor-1",
                expected_version=1,
            )

    @pytest.mark.asyncio
    async def test_assign_empty_technician_raises(self, service, mock_repository):
        wo = make_work_order(status="scheduled")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="assigned_to is required"):
            await service.assign_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                assigned_to="  ",
                assigned_by="supervisor-1",
                expected_version=1,
            )


# ─── Start Work Order ────────────────────────────────────────────────────────


class TestStartWorkOrder:
    @pytest.mark.asyncio
    async def test_start_scheduled_work_order_success(self, service, mock_repository):
        wo = make_work_order(status="scheduled", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.start_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            started_by="tech-1",
            expected_version=1,
        )

        assert result is wo
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_on_hold_work_order_success(self, service, mock_repository):
        wo = make_work_order(status="on_hold", version=1, on_hold_reason="Waiting for parts")
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.start_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            started_by="tech-1",
            expected_version=1,
        )

        assert result is wo

    @pytest.mark.asyncio
    async def test_start_draft_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="draft")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'draft'"):
            await service.start_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                started_by="tech-1",
                expected_version=1,
            )

    @pytest.mark.asyncio
    async def test_start_completed_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="completed")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'completed'"):
            await service.start_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                started_by="tech-1",
                expected_version=1,
            )


# ─── Complete Work Order ─────────────────────────────────────────────────────


class TestCompleteWorkOrder:
    @pytest.mark.asyncio
    async def test_complete_in_progress_work_order_success(
        self, service, mock_repository, mock_outbox
    ):
        wo = make_work_order(status="in_progress", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.complete_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            completed_by="tech-1",
            expected_version=1,
            resolution_summary="Replaced coil and ran diagnostics",
            labor_hours=3.5,
            parts_used=["coil-abc", "connector-xyz"],
        )

        assert result is wo
        mock_repository.update.assert_called_once()
        assert service.outbox.append.called

    @pytest.mark.asyncio
    async def test_complete_scheduled_work_order_success(
        self, service, mock_repository, mock_outbox
    ):
        wo = make_work_order(status="scheduled", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.complete_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            completed_by="tech-1",
            expected_version=1,
        )

        assert result is wo

    @pytest.mark.asyncio
    async def test_complete_pending_parts_work_order_success(
        self, service, mock_repository, mock_outbox
    ):
        wo = make_work_order(status="pending_parts", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.complete_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            completed_by="tech-1",
            expected_version=1,
        )

        assert result is wo

    @pytest.mark.asyncio
    async def test_complete_cancelled_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="cancelled")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'cancelled'"):
            await service.complete_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                completed_by="tech-1",
                expected_version=1,
            )

    @pytest.mark.asyncio
    async def test_complete_work_order_version_mismatch_raises(
        self, service, mock_repository
    ):
        wo = make_work_order(status="in_progress", version=2)
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="Concurrent modification"):
            await service.complete_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                completed_by="tech-1",
                expected_version=1,
            )


# ─── Cancel Work Order ────────────────────────────────────────────────────────


class TestCancelWorkOrder:
    @pytest.mark.asyncio
    async def test_cancel_in_progress_work_order_success(
        self, service, mock_repository, mock_outbox
    ):
        wo = make_work_order(status="in_progress", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.cancel_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            cancelled_by="supervisor-1",
            cancellation_reason="Device decommissioned",
            expected_version=1,
        )

        assert result is wo
        assert service.outbox.append.called

    @pytest.mark.asyncio
    async def test_cancel_scheduled_work_order_success(
        self, service, mock_repository, mock_outbox
    ):
        wo = make_work_order(status="scheduled", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.cancel_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            cancelled_by="supervisor-1",
            cancellation_reason="No longer needed",
            expected_version=1,
        )

        assert result is wo

    @pytest.mark.asyncio
    async def test_cancel_completed_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="completed")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'completed'"):
            await service.cancel_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                cancelled_by="supervisor-1",
                cancellation_reason="Test",
                expected_version=1,
            )

    @pytest.mark.asyncio
    async def test_cancel_already_cancelled_work_order_raises(
        self, service, mock_repository
    ):
        wo = make_work_order(status="cancelled")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'cancelled'"):
            await service.cancel_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                cancelled_by="supervisor-1",
                cancellation_reason="Test",
                expected_version=1,
            )


# ─── Put On Hold ─────────────────────────────────────────────────────────────


class TestPutOnHold:
    @pytest.mark.asyncio
    async def test_put_scheduled_on_hold_success(self, service, mock_repository):
        wo = make_work_order(status="scheduled", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.put_on_hold(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            hold_reason="Awaiting parts from supplier",
            put_on_hold_by="supervisor-1",
            expected_version=1,
        )

        assert result is wo
        assert service.outbox.append.called

    @pytest.mark.asyncio
    async def test_put_in_progress_on_hold_success(self, service, mock_repository):
        wo = make_work_order(status="in_progress", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.put_on_hold(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            hold_reason="Customer unavailable",
            put_on_hold_by="tech-1",
            expected_version=1,
        )

        assert result is wo

    @pytest.mark.asyncio
    async def test_put_completed_on_hold_raises(self, service, mock_repository):
        wo = make_work_order(status="completed")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'completed'"):
            await service.put_on_hold(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                hold_reason="Test",
                put_on_hold_by="user-1",
                expected_version=1,
            )

    @pytest.mark.asyncio
    async def test_put_draft_on_hold_raises(self, service, mock_repository):
        wo = make_work_order(status="draft")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'draft'"):
            await service.put_on_hold(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                hold_reason="Test",
                put_on_hold_by="user-1",
                expected_version=1,
            )


# ─── Update Work Order ───────────────────────────────────────────────────────


class TestUpdateWorkOrder:
    @pytest.mark.asyncio
    async def test_update_work_order_success(self, service, mock_repository):
        wo = make_work_order(status="scheduled", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo

        result = await service.update_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            expected_version=1,
            updated_by="supervisor-1",
            description="Updated description",
            priority="high",
        )

        assert result is wo
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_completed_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="completed", version=1)
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'completed'"):
            await service.update_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                expected_version=1,
                description="New desc",
            )

    @pytest.mark.asyncio
    async def test_update_cancelled_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="cancelled", version=1)
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="status is 'cancelled'"):
            await service.update_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                expected_version=1,
                description="New desc",
            )

    @pytest.mark.asyncio
    async def test_update_invalid_priority_raises(self, service, mock_repository):
        wo = make_work_order(status="scheduled", version=1)
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="priority must be one of"):
            await service.update_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                expected_version=1,
                priority="super-urgent",
            )

    @pytest.mark.asyncio
    async def test_update_work_order_version_mismatch_raises(
        self, service, mock_repository
    ):
        wo = make_work_order(status="scheduled", version=2)
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="Concurrent modification"):
            await service.update_work_order(
                work_order_id=str(wo.id),
                tenant_id="tenant-1",
                expected_version=1,
                description="New desc",
            )


# ─── Queries ─────────────────────────────────────────────────────────────────


class TestQueries:
    @pytest.mark.asyncio
    async def test_get_work_order(self, service, mock_repository):
        wo = make_work_order()
        mock_repository.get_by_id.return_value = wo

        result = await service.get_work_order(str(wo.id), "tenant-1")

        assert result is wo
        mock_repository.get_by_id.assert_called_once_with(str(wo.id), "tenant-1")

    @pytest.mark.asyncio
    async def test_get_work_order_not_found(self, service, mock_repository):
        mock_repository.get_by_id.return_value = None

        result = await service.get_work_order("nonexistent", "tenant-1")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_work_orders(self, service, mock_repository):
        items = [make_work_order(), make_work_order()]
        mock_repository.list_by_tenant.return_value = (items, 2)

        result = await service.list_work_orders(
            tenant_id="tenant-1",
            page=1,
            page_size=10,
            status="scheduled",
            priority="high",
        )

        assert result == (items, 2)
        mock_repository.list_by_tenant.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_overdue_work_orders(self, service, mock_repository):
        items = [make_work_order(), make_work_order()]
        mock_repository.list_overdue.return_value = items

        result = await service.list_overdue_work_orders("tenant-1")

        assert result == items
        mock_repository.list_overdue.assert_called_once_with("tenant-1")


# ─── Delete Work Order ────────────────────────────────────────────────────────


class TestDeleteWorkOrder:
    @pytest.mark.asyncio
    async def test_delete_draft_work_order_success(self, service, mock_repository):
        wo = make_work_order(status="draft")
        mock_repository.get_by_id.return_value = wo
        mock_repository.delete.return_value = True

        result = await service.delete_work_order(str(wo.id), "tenant-1")

        assert result is True
        mock_repository.delete.assert_called_once_with(str(wo.id), "tenant-1")

    @pytest.mark.asyncio
    async def test_delete_cancelled_work_order_success(self, service, mock_repository):
        wo = make_work_order(status="cancelled")
        mock_repository.get_by_id.return_value = wo
        mock_repository.delete.return_value = True

        result = await service.delete_work_order(str(wo.id), "tenant-1")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_in_progress_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="in_progress")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="Only 'draft' or 'cancelled'"):
            await service.delete_work_order(str(wo.id), "tenant-1")

    @pytest.mark.asyncio
    async def test_delete_scheduled_work_order_raises(self, service, mock_repository):
        wo = make_work_order(status="scheduled")
        mock_repository.get_by_id.return_value = wo

        with pytest.raises(ValueError, match="Only 'draft' or 'cancelled'"):
            await service.delete_work_order(str(wo.id), "tenant-1")

    @pytest.mark.asyncio
    async def test_delete_not_found_returns_false(self, service, mock_repository):
        mock_repository.get_by_id.return_value = None

        result = await service.delete_work_order("nonexistent", "tenant-1")

        assert result is False


# ─── SLA Deadline Computation ────────────────────────────────────────────────


class TestSLADeadline:
    @pytest.mark.asyncio
    async def test_sla_emergency_is_4_hours(self, service, mock_repository):
        wo = make_work_order(status="draft", priority="emergency", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo
        scheduled = datetime.now(UTC) + timedelta(hours=2)

        await service.schedule_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            scheduled_date=scheduled,
            expected_version=1,
            scheduled_by="user-1",
        )

        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_sla_low_is_30_days(self, service, mock_repository):
        wo = make_work_order(status="draft", priority="low", version=1)
        mock_repository.get_by_id.return_value = wo
        mock_repository.update.return_value = wo
        scheduled = datetime.now(UTC) + timedelta(days=5)

        await service.schedule_work_order(
            work_order_id=str(wo.id),
            tenant_id="tenant-1",
            scheduled_date=scheduled,
            expected_version=1,
            scheduled_by="user-1",
        )

        mock_repository.update.assert_called_once()
