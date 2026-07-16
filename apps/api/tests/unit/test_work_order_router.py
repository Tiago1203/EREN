"""API tests for the Work Order lifecycle router.

Tests all REST endpoints with mocked services and database sessions.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest


class FakeWorkOrder:
    """Fake work order model matching the response schema."""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid4())
        self.tenant_id = kwargs.get("tenant_id", "tenant-1")
        self.device_id = kwargs.get("device_id", uuid4())
        self.work_order_type = kwargs.get("work_order_type", "corrective")
        self.description = kwargs.get("description", "Test maintenance")
        self.notes = kwargs.get("notes")
        self.resolution_summary = kwargs.get("resolution_summary")
        self.cancellation_reason = kwargs.get("cancellation_reason")
        self.priority = kwargs.get("priority", "medium")
        self.status = kwargs.get("status", "draft")
        self.assigned_to = kwargs.get("assigned_to")
        self.assigned_by = kwargs.get("assigned_by")
        self.assigned_at = kwargs.get("assigned_at")
        self.scheduled_date = kwargs.get("scheduled_date")
        self.estimated_duration_hours = kwargs.get("estimated_duration_hours")
        self.actual_labor_hours = kwargs.get("actual_labor_hours")
        self.started_at = kwargs.get("started_at")
        self.completed_at = kwargs.get("completed_at")
        self.completed_by = kwargs.get("completed_by")
        self.sla_deadline = kwargs.get("sla_deadline")
        self.sla_breached = kwargs.get("sla_breached", "false")
        self.on_hold_reason = kwargs.get("on_hold_reason")
        self.on_hold_at = kwargs.get("on_hold_at")
        self.incident_id = kwargs.get("incident_id")
        self.preventive_schedule_id = kwargs.get("preventive_schedule_id")
        self.parts_used = kwargs.get("parts_used")
        self.next_calibration_date = kwargs.get("next_calibration_date")
        self.created_at = kwargs.get("created_at", datetime.now(UTC))
        self.updated_at = kwargs.get("updated_at", datetime.now(UTC))
        self.created_by = kwargs.get("created_by", "user-1")
        self.cancelled_by = kwargs.get("cancelled_by")
        self.version = kwargs.get("version", 1)


def make_app(work_order_service=None, db_session=None):
    """Build a test app with mocked dependencies."""
    from unittest.mock import AsyncMock

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from apps.api.app.routers.work_orders import (
        get_correlation_id,
        get_current_user_id,
        get_db,
        get_tenant_id,
        get_work_order_service,
        router,
    )

    app = FastAPI()

    _wo_service = work_order_service or AsyncMock()

    def _get_work_order_service():
        return _wo_service

    def _get_db():
        return db_session or AsyncMock()

    def _mock_get_tenant_id() -> str:
        return "tenant-1"

    def _mock_get_current_user_id() -> str | None:
        return "user-1"

    def _mock_get_correlation_id() -> str | None:
        return "test-req-1"

    app.include_router(router)

    app.dependency_overrides[get_work_order_service] = _get_work_order_service
    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_tenant_id] = _mock_get_tenant_id
    app.dependency_overrides[get_current_user_id] = _mock_get_current_user_id
    app.dependency_overrides[get_correlation_id] = _mock_get_correlation_id

    return TestClient(app)


def _wo_response(wo=None, **overrides):
    """Return a work order response dict matching WorkOrderResponse schema."""
    d = wo or FakeWorkOrder(**overrides)
    return {
        "id": str(d.id),
        "tenant_id": d.tenant_id,
        "device_id": str(d.device_id),
        "work_order_type": d.work_order_type,
        "description": d.description,
        "notes": d.notes,
        "resolution_summary": d.resolution_summary,
        "cancellation_reason": d.cancellation_reason,
        "priority": d.priority,
        "status": d.status,
        "assigned_to": d.assigned_to,
        "assigned_by": d.assigned_by,
        "assigned_at": d.assigned_at.isoformat() if d.assigned_at else None,
        "scheduled_date": d.scheduled_date.isoformat() if d.scheduled_date else None,
        "estimated_duration_hours": d.estimated_duration_hours,
        "actual_labor_hours": d.actual_labor_hours,
        "started_at": d.started_at.isoformat() if d.started_at else None,
        "completed_at": d.completed_at.isoformat() if d.completed_at else None,
        "completed_by": d.completed_by,
        "sla_deadline": d.sla_deadline.isoformat() if d.sla_deadline else None,
        "sla_breached": d.sla_breached,
        "on_hold_reason": d.on_hold_reason,
        "on_hold_at": d.on_hold_at.isoformat() if d.on_hold_at else None,
        "incident_id": str(d.incident_id) if d.incident_id else None,
        "preventive_schedule_id": d.preventive_schedule_id,
        "parts_used": d.parts_used,
        "next_calibration_date": (
            d.next_calibration_date.isoformat() if d.next_calibration_date else None
        ),
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        "created_by": d.created_by,
        "cancelled_by": d.cancelled_by,
        "version": d.version,
    }


# ─── Create Work Order ─────────────────────────────────────────────────────────


class TestCreateWorkOrder:
    def test_create_work_order_success(self):
        wo = FakeWorkOrder()
        service = AsyncMock()
        service.create_work_order.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.post(
            "/work-orders",
            json={
                "device_id": str(wo.device_id),
                "device_name": "MRI Scanner",
                "device_serial": "SN-001",
                "work_order_type": "corrective",
                "description": "Replace faulty coil",
                "priority": "high",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "medium"  # FakeWorkOrder default
        assert data["status"] == "draft"
        assert data["description"] == "Test maintenance"
        db.commit.assert_called()

    def test_create_work_order_invalid_type_returns_422(self):
        service = AsyncMock()
        app = make_app(work_order_service=service)

        response = app.post(
            "/work-orders",
            json={
                "device_id": str(uuid4()),
                "device_name": "MRI Scanner",
                "device_serial": "SN-001",
                "work_order_type": "invalid_type",
                "description": "Test",
                "priority": "medium",
            },
        )

        assert response.status_code == 422  # Pydantic validates work_order_type enum

    def test_create_work_order_empty_description_returns_422(self):
        service = AsyncMock()
        app = make_app(work_order_service=service)

        response = app.post(
            "/work-orders",
            json={
                "device_id": str(uuid4()),
                "device_name": "MRI Scanner",
                "device_serial": "SN-001",
                "work_order_type": "corrective",
                "description": "",
                "priority": "medium",
            },
        )

        assert response.status_code == 422

    def test_create_work_order_service_raises_400(self):
        service = AsyncMock()
        service.create_work_order.side_effect = ValueError("device_id is required")
        app = make_app(work_order_service=service)

        response = app.post(
            "/work-orders",
            json={
                "device_id": str(uuid4()),
                "device_name": "MRI Scanner",
                "device_serial": "SN-001",
                "work_order_type": "corrective",
                "description": "Test",
                "priority": "medium",
            },
        )

        assert response.status_code == 400
        assert "device_id is required" in response.json()["detail"]


# ─── List Work Orders ─────────────────────────────────────────────────────────


class TestListWorkOrders:
    def test_list_work_orders_success(self):
        items = [FakeWorkOrder(), FakeWorkOrder()]
        service = AsyncMock()
        service.list_work_orders.return_value = (items, 2)
        app = make_app(work_order_service=service)

        response = app.get("/work-orders?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_work_orders_with_filters(self):
        items = [FakeWorkOrder(status="scheduled", priority="high")]
        service = AsyncMock()
        service.list_work_orders.return_value = (items, 1)
        app = make_app(work_order_service=service)

        response = app.get("/work-orders?status=scheduled&priority=high&device_id=abc")

        assert response.status_code == 200
        service.list_work_orders.assert_called_once()
        call_kwargs = service.list_work_orders.call_args.kwargs
        assert call_kwargs["status"] == "scheduled"
        assert call_kwargs["priority"] == "high"
        assert call_kwargs["device_id"] == "abc"


# ─── Get Work Order ───────────────────────────────────────────────────────────


class TestGetWorkOrder:
    def test_get_work_order_success(self):
        wo = FakeWorkOrder()
        service = AsyncMock()
        service.get_work_order.return_value = wo
        app = make_app(work_order_service=service)

        response = app.get(f"/work-orders/{wo.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(wo.id)

    def test_get_work_order_not_found_returns_404(self):
        service = AsyncMock()
        service.get_work_order.return_value = None
        app = make_app(work_order_service=service)

        response = app.get(f"/work-orders/{uuid4()}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


# ─── Update Work Order ────────────────────────────────────────────────────────


class TestUpdateWorkOrder:
    def test_update_work_order_success(self):
        wo = FakeWorkOrder(status="scheduled", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.update_work_order.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.patch(
            f"/work-orders/{wo.id}",
            json={"description": "Updated description", "priority": "urgent"},
        )

        assert response.status_code == 200
        db.commit.assert_called()

    def test_update_work_order_not_found_returns_404(self):
        service = AsyncMock()
        service.get_work_order.return_value = None
        app = make_app(work_order_service=service)

        response = app.patch(f"/work-orders/{uuid4()}", json={"description": "Test"})

        assert response.status_code == 404

    def test_update_work_order_concurrent_returns_409(self):
        wo = FakeWorkOrder(status="scheduled", version=2)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.update_work_order.side_effect = ValueError(
            "Work order version mismatch: expected 1, found 2"
        )
        app = make_app(work_order_service=service)

        response = app.patch(
            f"/work-orders/{wo.id}",
            json={"description": "Updated"},
        )

        assert response.status_code == 409
        assert "version mismatch" in response.json()["detail"]


# ─── Schedule Work Order ──────────────────────────────────────────────────────


class TestScheduleWorkOrder:
    def test_schedule_work_order_success(self):
        wo = FakeWorkOrder(status="draft", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.schedule_work_order.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)
        scheduled = (datetime.now(UTC) + timedelta(days=3)).isoformat()

        response = app.post(
            f"/work-orders/{wo.id}/schedule",
            json={"scheduled_date": scheduled, "estimated_duration_hours": 4.0},
        )

        assert response.status_code == 200
        db.commit.assert_called()

    def test_schedule_work_order_wrong_status_returns_400(self):
        wo = FakeWorkOrder(status="completed", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.schedule_work_order.side_effect = ValueError(
            "Cannot schedule work order: status is 'completed', expected 'draft'."
        )
        app = make_app(work_order_service=service)

        response = app.post(
            f"/work-orders/{wo.id}/schedule",
            json={"scheduled_date": (datetime.now(UTC) + timedelta(days=1)).isoformat()},
        )

        assert response.status_code == 400


# ─── Assign Work Order ────────────────────────────────────────────────────────


class TestAssignWorkOrder:
    def test_assign_work_order_success(self):
        wo = FakeWorkOrder(status="scheduled", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.assign_work_order.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.post(
            f"/work-orders/{wo.id}/assign",
            json={"assigned_to": "tech-2"},
        )

        assert response.status_code == 200

    def test_assign_work_order_empty_returns_422(self):
        service = AsyncMock()
        app = make_app(work_order_service=service)

        response = app.post(
            f"/work-orders/{uuid4()}/assign",
            json={"assigned_to": ""},
        )

        assert response.status_code == 422


# ─── Start Work Order ─────────────────────────────────────────────────────────


class TestStartWorkOrder:
    def test_start_work_order_success(self):
        wo = FakeWorkOrder(status="scheduled", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.start_work_order.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.post(f"/work-orders/{wo.id}/start")

        assert response.status_code == 200

    def test_start_work_order_wrong_status_returns_400(self):
        wo = FakeWorkOrder(status="completed", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.start_work_order.side_effect = ValueError(
            "Cannot start work order: status is 'completed', expected 'scheduled'."
        )
        app = make_app(work_order_service=service)

        response = app.post(f"/work-orders/{wo.id}/start")

        assert response.status_code == 400


# ─── Complete Work Order ───────────────────────────────────────────────────────


class TestCompleteWorkOrder:
    def test_complete_work_order_success(self):
        wo = FakeWorkOrder(status="in_progress", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.complete_work_order.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.post(
            f"/work-orders/{wo.id}/complete",
            json={
                "resolution_summary": "Replaced coil successfully",
                "parts_used": ["coil-abc"],
                "labor_hours": 3.5,
            },
        )

        assert response.status_code == 200

    def test_complete_work_order_empty_body_success(self):
        wo = FakeWorkOrder(status="in_progress", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.complete_work_order.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.post(f"/work-orders/{wo.id}/complete", json={})

        assert response.status_code == 200


# ─── Cancel Work Order ────────────────────────────────────────────────────────


class TestCancelWorkOrder:
    def test_cancel_work_order_success(self):
        wo = FakeWorkOrder(status="scheduled", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.cancel_work_order.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.post(
            f"/work-orders/{wo.id}/cancel",
            json={"cancellation_reason": "No longer needed"},
        )

        assert response.status_code == 200

    def test_cancel_work_order_empty_reason_returns_422(self):
        service = AsyncMock()
        app = make_app(work_order_service=service)

        response = app.post(
            f"/work-orders/{uuid4()}/cancel",
            json={"cancellation_reason": ""},
        )

        assert response.status_code == 422


# ─── Put On Hold ──────────────────────────────────────────────────────────────


class TestPutOnHold:
    def test_put_on_hold_success(self):
        wo = FakeWorkOrder(status="in_progress", version=1)
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.put_on_hold.return_value = wo
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.post(
            f"/work-orders/{wo.id}/hold",
            json={"hold_reason": "Awaiting replacement parts"},
        )

        assert response.status_code == 200

    def test_put_on_hold_empty_reason_returns_422(self):
        service = AsyncMock()
        app = make_app(work_order_service=service)

        response = app.post(
            f"/work-orders/{uuid4()}/hold",
            json={"hold_reason": ""},
        )

        assert response.status_code == 422


# ─── Delete Work Order ────────────────────────────────────────────────────────


class TestDeleteWorkOrder:
    def test_delete_work_order_success(self):
        wo = FakeWorkOrder(status="draft")
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.delete_work_order.return_value = True
        db = AsyncMock()
        app = make_app(work_order_service=service, db_session=db)

        response = app.delete(f"/work-orders/{wo.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True

    def test_delete_work_order_not_found_returns_404(self):
        service = AsyncMock()
        service.get_work_order.return_value = None
        service.delete_work_order.return_value = False
        app = make_app(work_order_service=service)

        response = app.delete(f"/work-orders/{uuid4()}")

        assert response.status_code == 404

    def test_delete_work_order_invalid_status_returns_400(self):
        wo = FakeWorkOrder(status="in_progress")
        service = AsyncMock()
        service.get_work_order.return_value = wo
        service.delete_work_order.side_effect = ValueError(
            "Only 'draft' or 'cancelled' work orders can be deleted"
        )
        app = make_app(work_order_service=service)

        response = app.delete(f"/work-orders/{wo.id}")

        assert response.status_code == 400


# ─── Overdue Work Orders ──────────────────────────────────────────────────────


class TestOverdueWorkOrders:
    def test_list_overdue_work_orders(self):
        items = [FakeWorkOrder(), FakeWorkOrder()]
        service = AsyncMock()
        service.list_overdue_work_orders.return_value = items
        app = make_app(work_order_service=service)

        response = app.get("/work-orders/overdue/list")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2


# ─── Tenant Isolation ─────────────────────────────────────────────────────────


class TestTenantIsolation:
    def test_tenant_not_resolved_returns_403(self):
        from unittest.mock import MagicMock

        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from apps.api.app.routers.work_orders import (
            get_correlation_id,
            get_current_user_id,
            get_db,
            get_tenant_id,
            get_work_order_service,
            router,
        )

        app = FastAPI()
        app.include_router(router)

        def _no_tenant():
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")

        app.dependency_overrides[get_work_order_service] = lambda: AsyncMock()
        app.dependency_overrides[get_db] = lambda: AsyncMock()
        app.dependency_overrides[get_tenant_id] = _no_tenant
        app.dependency_overrides[get_current_user_id] = lambda: "user-1"
        app.dependency_overrides[get_correlation_id] = lambda: "test-1"

        client = TestClient(app)

        response = client.get("/work-orders")

        assert response.status_code == 403
