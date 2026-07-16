"""API tests for the device lifecycle router.

Tests all REST endpoints with mocked services and database sessions.
Covers: CRUD, lifecycle operations, error handling, RBAC, optimistic locking.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class FakeDevice:
    """Fake device model matching the response schema."""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid4())
        self.tenant_id = kwargs.get("tenant_id", "tenant-1")
        self.serial_number = kwargs.get("serial_number", "SN-001")
        self.manufacturer_name = kwargs.get("manufacturer_name", "Acme")
        self.manufacturer_model = kwargs.get("manufacturer_model", "X-100")
        self.manufacturer_country = kwargs.get("manufacturer_country", "USA")
        self.device_type = kwargs.get("device_type", "diagnostic")
        self.name = kwargs.get("name", "Test Device")
        self.description = kwargs.get("description")
        self.is_critical = kwargs.get("is_critical", False)
        self.status = kwargs.get("status", "registered")
        self.location_building = kwargs.get("location_building", "Main")
        self.location_floor = kwargs.get("location_floor", "1")
        self.location_room = kwargs.get("location_room", "101")
        self.location_department = kwargs.get("location_department", "Radiology")
        self.calibration_last = kwargs.get("calibration_last")
        self.calibration_next = kwargs.get("calibration_next")
        self.calibration_interval_days = kwargs.get("calibration_interval_days")
        self.maintenance_interval_days = kwargs.get("maintenance_interval_days")
        self.notes = kwargs.get("notes")
        self.registered_at = kwargs.get("registered_at", datetime.now(UTC))
        self.registered_by = kwargs.get("registered_by", "engineer-1")
        self.last_status_change = kwargs.get("last_status_change", datetime.now(UTC))
        self.version = kwargs.get("version", 1)
        self.created_at = kwargs.get("created_at", datetime.now(UTC))
        self.updated_at = kwargs.get("updated_at", datetime.now(UTC))


def make_app(device_service=None, cache_service=None, db_session=None):
    """Build a test app with mocked dependencies.

    Override functions must NOT have request: Request parameters to avoid
    FastAPI's recursive dependency resolution (request: Request triggers auto-injection
    which leads to infinite loops when the override function itself is resolved).
    """
    from unittest.mock import AsyncMock

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from apps.api.app.routers.devices import (
        get_correlation_id,
        get_current_user_id,
        get_device_cache,
        get_device_service,
        get_db,
        get_tenant_id,
        router,
    )

    app = FastAPI()

    _device_service = device_service or AsyncMock()

    def _get_device_service():
        return _device_service

    def _get_device_cache():
        return cache_service or AsyncMock()

    def _get_db():
        return db_session or AsyncMock()

    # NOTE: Override functions must NOT have request: Request parameters.
    # FastAPI's request: Request auto-injection causes infinite recursion
    # when the override function itself is a dependency of the endpoint.
    def _mock_get_tenant_id() -> str:
        return "tenant-1"

    def _mock_get_current_user_id() -> str | None:
        return "user-1"

    def _mock_get_correlation_id() -> str | None:
        return "test-req-1"

    # Include router FIRST (before setting overrides)
    app.include_router(router)

    # Then set overrides
    app.dependency_overrides[get_device_service] = _get_device_service
    app.dependency_overrides[get_device_cache] = _get_device_cache
    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_tenant_id] = _mock_get_tenant_id
    app.dependency_overrides[get_current_user_id] = _mock_get_current_user_id
    app.dependency_overrides[get_correlation_id] = _mock_get_correlation_id

    return TestClient(app)


def make_fake_request(tenant_id="tenant-1", user_id="user-1", request_id="req-1"):
    """Build a fake request with state attributes."""
    from types import SimpleNamespace

    req = SimpleNamespace()
    req.state = SimpleNamespace(
        tenant_id=tenant_id, principal=SimpleNamespace(principal_id=user_id), request_id=request_id
    )
    return req


# ─── Helper ────────────────────────────────────────────────────────────────────


def _device_response(device=None, **overrides):
    """Return a device response dict."""
    d = device or FakeDevice(**overrides)
    return {
        "id": str(d.id),
        "tenant_id": d.tenant_id,
        "serial_number": d.serial_number,
        "manufacturer_name": d.manufacturer_name,
        "manufacturer_model": d.manufacturer_model,
        "manufacturer_country": d.manufacturer_country,
        "device_type": d.device_type,
        "name": d.name,
        "description": d.description,
        "is_critical": d.is_critical,
        "status": d.status,
        "location_building": d.location_building,
        "location_floor": d.location_floor,
        "location_room": d.location_room,
        "location_department": d.location_department,
        "calibration_last": d.calibration_last,
        "calibration_next": d.calibration_next,
        "calibration_interval_days": d.calibration_interval_days,
        "maintenance_interval_days": d.maintenance_interval_days,
        "notes": d.notes,
        "registered_at": d.registered_at.isoformat() if d.registered_at else None,
        "registered_by": d.registered_by,
        "last_status_change": d.last_status_change.isoformat() if d.last_status_change else None,
        "version": d.version,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    }


# ─── POST /devices ──────────────────────────────────────────────────────────────


class TestRegisterDevice:
    def test_register_device_success(self):
        device = FakeDevice()
        service = AsyncMock()
        service.register_device = AsyncMock(return_value=device)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            "/devices",
            json={
                "serial_number": "SN-API-001",
                "name": "API Test Device",
                "device_type": "diagnostic",
                "manufacturer_name": "Acme",
                "manufacturer_model": "X-100",
                "manufacturer_country": "USA",
                "building": "Main",
                "floor": "1",
                "room": "101",
                "department": "Radiology",
                "is_critical": False,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        # The mock returns a FakeDevice with default serial_number="SN-001"
        assert body["serial_number"] == "SN-001"
        assert body["name"] == "Test Device"

    def test_register_device_validation_error(self):
        service = AsyncMock()
        service.register_device = AsyncMock(side_effect=ValueError("Serial number required"))
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post("/devices", json={"name": "No Serial"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_device_duplicate_serial(self):
        service = AsyncMock()
        service.register_device = AsyncMock(
        side_effect=ValueError("Serial number 'SN-DUP' already in use")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            "/devices",
            json={
                "serial_number": "SN-DUP",
                "name": "Duplicate",
                "device_type": "diagnostic",
                "manufacturer_name": "Acme",
                "manufacturer_model": "X-100",
                "building": "Main",
                "department": "Radiology",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already in use" in response.json()["detail"]


# ─── GET /devices ──────────────────────────────────────────────────────────────


class TestListDevices:
    def test_list_devices_empty(self):
        service = AsyncMock()
        service.list_devices = AsyncMock(return_value=([], 0))
        client = make_app(device_service=service)

        response = client.get("/devices")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["items"] == []
        assert body["total"] == 0
        assert body["page"] == 1

    def test_list_devices_with_results(self):
        devices = [FakeDevice(serial_number=f"SN-{i:03d}") for i in range(3)]
        service = AsyncMock()
        service.list_devices = AsyncMock(return_value=(devices, 3))
        client = make_app(device_service=service)

        response = client.get("/devices?page=1&page_size=2&status=active")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert len(body["items"]) == 3
        assert body["total"] == 3
        assert body["pages"] == 2

    def test_list_devices_with_search(self):
        devices = [FakeDevice(name="MRI Scanner")]
        service = AsyncMock()
        service.list_devices = AsyncMock(return_value=(devices, 1))
        client = make_app(device_service=service)

        response = client.get("/devices?search=MRI")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["items"]) == 1

    def test_list_devices_pagination(self):
        service = AsyncMock()
        service.list_devices = AsyncMock(return_value=([], 0))
        client = make_app(device_service=service)

        response = client.get("/devices?page=5&page_size=10")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["page"] == 5


# ─── GET /devices/{id} ────────────────────────────────────────────────────────


class TestGetDevice:
    def test_get_device_found(self):
        device = FakeDevice()
        service = AsyncMock()
        service.get_device = AsyncMock(return_value=device)
        cache = AsyncMock()
        cache.get_by_id = AsyncMock(return_value=None)  # cache miss
        client = make_app(device_service=service, cache_service=cache)

        response = client.get(f"/devices/{device.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(device.id)

    def test_get_device_from_cache(self):
        device = FakeDevice()
        cache = AsyncMock()
        cache.get_by_id = AsyncMock(return_value=_device_response(device))
        service = AsyncMock()
        client = make_app(device_service=service, cache_service=cache)

        response = client.get(f"/devices/{device.id}")

        assert response.status_code == status.HTTP_200_OK
        service.get_device.assert_not_called()  # served from cache

    def test_get_device_not_found(self):
        service = AsyncMock()
        service.get_device = AsyncMock(return_value=None)
        cache = AsyncMock()
        cache.get_by_id = AsyncMock(return_value=None)
        client = make_app(device_service=service, cache_service=cache)

        response = client.get("/devices/nonexistent-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ─── PATCH /devices/{id} ──────────────────────────────────────────────────────


class TestUpdateDevice:
    def test_update_device_success(self):
        device = FakeDevice(version=2)
        service = AsyncMock()
        service.update_device = AsyncMock(return_value=device)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.patch(
            f"/devices/{device.id}",
            json={"name": "Updated Name", "version": 1},
        )

        assert response.status_code == status.HTTP_200_OK
        # The mock returns a FakeDevice with default name="Test Device"
        assert response.json()["name"] == "Test Device"
        assert response.json()["version"] == 2

    def test_update_device_not_found(self):
        service = AsyncMock()
        service.update_device = AsyncMock(side_effect=ValueError("Device not found"))
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.patch(
            "/devices/nonexistent",
            json={"name": "Updated", "version": 1},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_device_version_conflict(self):
        device = FakeDevice()
        service = AsyncMock()
        service.update_device = AsyncMock(
        side_effect=ValueError("Device version mismatch: expected 1, found 2")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.patch(
            f"/devices/{device.id}",
            json={"name": "Stale Update", "version": 1},
        )

        assert response.status_code == status.HTTP_409_CONFLICT


# ─── DELETE /devices/{id} ──────────────────────────────────────────────────────


class TestDeleteDevice:
    def test_delete_device_success(self):
        device = FakeDevice()
        service = AsyncMock()
        service.delete_device = AsyncMock(return_value=True)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.delete(f"/devices/{device.id}?version={device.version}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["deleted"] is True

    def test_delete_device_not_found(self):
        service = AsyncMock()
        service.delete_device = AsyncMock(return_value=False)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.delete("/devices/nonexistent?version=1")

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ─── POST /devices/{id}/transfer ───────────────────────────────────────────────


class TestTransferDevice:
    def test_transfer_device_success(self):
        device = FakeDevice(location_building="Building A")
        updated = FakeDevice(location_building="Building B", version=2)
        service = AsyncMock()
        service.transfer_device = AsyncMock(return_value=updated)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/transfer",
            json={
                "building": "Building B",
                "floor": "3",
                "room": "301",
                "department": "ICU",
                "reason": "Relocation",
                "version": 1,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["location_building"] == "Building B"

    def test_transfer_decommissioned_raises(self):
        device = FakeDevice()
        service = AsyncMock()
        service.transfer_device = AsyncMock(
        side_effect=ValueError("Cannot transfer decommissioned device")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/transfer",
            json={"building": "B", "version": 1},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── POST /devices/{id}/maintenance ───────────────────────────────────────────


class TestScheduleMaintenance:
    def test_schedule_maintenance_success(self):
        device = FakeDevice()
        service = AsyncMock()
        service.schedule_maintenance = AsyncMock(return_value=device)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/maintenance",
            json={
                "maintenance_type": "preventive",
                "scheduled_date": "2026-08-01",
                "estimated_duration_hours": 2,
                "technician_id": "tech-1",
                "version": 1,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(device.id)

    def test_schedule_maintenance_while_in_maintenance_raises(self):
        device = FakeDevice()
        service = AsyncMock()
        service.schedule_maintenance = AsyncMock(
        side_effect=ValueError("Device already in maintenance")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/maintenance",
            json={"maintenance_type": "preventive", "scheduled_date": "2026-08-01", "version": 1},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── POST /devices/{id}/maintenance/start ─────────────────────────────────────


class TestStartMaintenance:
    def test_start_maintenance_success(self):
        device = FakeDevice(status="active")
        updated = FakeDevice(status="in_maintenance", version=2)
        service = AsyncMock()
        service.start_maintenance = AsyncMock(return_value=updated)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/maintenance/start",
            json={"maintenance_type": "corrective", "technician_id": "tech-1", "version": 1},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "in_maintenance"

    def test_start_maintenance_not_found(self):
        service = AsyncMock()
        service.start_maintenance = AsyncMock(side_effect=ValueError("Device not found"))
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            "/devices/nonexistent/maintenance/start",
            json={"maintenance_type": "corrective", "technician_id": "tech-1", "version": 1},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ─── POST /devices/{id}/maintenance/finish ─────────────────────────────────────


class TestFinishMaintenance:
    def test_finish_maintenance_success(self):
        device = FakeDevice(status="in_maintenance")
        updated = FakeDevice(status="active", version=2)
        service = AsyncMock()
        service.finish_maintenance = AsyncMock(return_value=updated)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/maintenance/finish",
            json={"version": 1},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "active"

    def test_finish_maintenance_not_in_maintenance_raises(self):
        device = FakeDevice(status="active")
        service = AsyncMock()
        service.finish_maintenance = AsyncMock(
        side_effect=ValueError("Device is not in maintenance")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/maintenance/finish",
            json={"version": 1},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── POST /devices/{id}/calibrate ─────────────────────────────────────────────


class TestCalibrateDevice:
    def test_calibrate_device_success(self):
        device = FakeDevice()
        updated = FakeDevice(version=2)
        service = AsyncMock()
        service.calibrate_device = AsyncMock(return_value=updated)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/calibrate",
            json={
                "calibration_last": "2026-01-01T00:00:00Z",
                "calibration_next": "2027-01-01T00:00:00Z",
                "calibration_interval_days": 365,
                "calibration_certificate": "CERT-001",
                "version": 1,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["version"] == 2

    def test_calibrate_decommissioned_raises(self):
        device = FakeDevice()
        service = AsyncMock()
        service.calibrate_device = AsyncMock(
        side_effect=ValueError("Cannot calibrate decommissioned device")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/calibrate",
            json={
                "calibration_last": "2026-01-01T00:00:00Z",
                "calibration_next": "2027-01-01T00:00:00Z",
                "calibration_interval_days": 365,
                "version": 1,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── POST /devices/{id}/out-of-service ────────────────────────────────────────


class TestOutOfService:
    def test_take_out_of_service_success(self):
        import json as _json
        device = FakeDevice(status="active")
        updated = FakeDevice(status="out_of_service", version=2)
        service = AsyncMock()
        service.take_out_of_service = AsyncMock(return_value=updated)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/out-of-service",
            json={"reason": "Scheduled inspection", "version": 1},
        )
        if response.status_code != 200:
            print(f"DEBUG: {response.status_code} - {_json.dumps(response.json(), indent=2)}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "out_of_service"

    def test_take_out_of_service_already_out_raises(self):
        device = FakeDevice()
        service = AsyncMock()
        service.take_out_of_service = AsyncMock(
        side_effect=ValueError("Device is already out of service")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/out-of-service",
            json={"reason": "Inspection", "version": 1},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── POST /devices/{id}/return-service ────────────────────────────────────────


class TestReturnToService:
    def test_return_to_service_success(self):
        device = FakeDevice(status="out_of_service")
        updated = FakeDevice(status="active", version=2)
        service = AsyncMock()
        service.return_to_service = AsyncMock(return_value=updated)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/return-service",
            json={"version": 1},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "active"

    def test_return_to_service_no_calibration_raises(self):
        device = FakeDevice()
        service = AsyncMock()
        service.return_to_service = AsyncMock(
        side_effect=ValueError("Cannot return to service: no calibration date set")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/return-service",
            json={"version": 1},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── POST /devices/{id}/decommission ──────────────────────────────────────────


class TestDecommission:
    def test_decommission_device_success(self):
        device = FakeDevice()
        updated = FakeDevice(status="decommissioned", version=2)
        service = AsyncMock()
        service.decommission_device = AsyncMock(return_value=updated)
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/decommission",
            json={"reason": "End of useful life", "version": 1},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "decommissioned"

    def test_decommission_already_decommissioned_raises(self):
        device = FakeDevice()
        service = AsyncMock()
        service.decommission_device = AsyncMock(
        side_effect=ValueError("Device is already decommissioned")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/decommission",
            json={"reason": "End of life", "version": 1},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_decommission_version_conflict(self):
        device = FakeDevice()
        service = AsyncMock()
        service.decommission_device = AsyncMock(
        side_effect=ValueError("Concurrent modification detected")
        )
        cache = AsyncMock()
        db = AsyncMock()
        client = make_app(device_service=service, cache_service=cache, db_session=db)

        response = client.post(
            f"/devices/{device.id}/decommission",
            json={"reason": "End of life", "version": 1},
        )

        assert response.status_code == status.HTTP_409_CONFLICT


# ─── RBAC / Tenant Isolation ───────────────────────────────────────────────────


class TestRBAC:
    def test_tenant_not_resolved_returns_403(self):
        from fastapi import FastAPI, HTTPException
        from fastapi.testclient import TestClient

        from apps.api.app.routers.devices import get_tenant_id, router

        app = FastAPI()

        def _broken_tenant_id() -> str:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")

        app.include_router(router)
        app.dependency_overrides[get_tenant_id] = _broken_tenant_id
        client = TestClient(app)

        response = client.get("/devices")
        assert response.status_code == status.HTTP_403_FORBIDDEN
