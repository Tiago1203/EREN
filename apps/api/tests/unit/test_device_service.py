"""Unit tests for DeviceService.

Tests the application service layer for device lifecycle operations.
Uses mocked repository and outbox.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.device import (
    DeviceService,
)
from app.domain.device.repository import DeviceRepository


class FakeDevice:
    """Fake device model for testing."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FakeOutbox:
    """Fake TransactionalOutbox for testing."""

    def __init__(self):
        self.appended: list[dict] = []

    def append(
        self,
        event_type: str,
        payload: dict,
        aggregate_type: str,
        correlation_id: str | None = None,
    ) -> None:
        self.appended.append({
            "event_type": event_type,
            "payload": payload,
            "aggregate_type": aggregate_type,
            "correlation_id": correlation_id,
        })


# ─── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def fake_outbox() -> FakeOutbox:
    return FakeOutbox()


@pytest.fixture
def mock_repository() -> AsyncMock:
    repo = AsyncMock(spec=DeviceRepository)
    return repo


@pytest.fixture
def device_service(mock_repository: AsyncMock, fake_outbox: FakeOutbox) -> DeviceService:
    return DeviceService(repository=mock_repository, outbox=fake_outbox)


def make_device(
    device_id: str | None = None,
    tenant_id: str = "tenant-1",
    serial: str = "SN-001",
    status: str = "registered",
    version: int = 1,
    **overrides,
) -> FakeDevice:
    defaults = dict(
        id=uuid4() if device_id is None else device_id,
        tenant_id=tenant_id,
        serial_number=serial,
        manufacturer_name="Acme",
        manufacturer_model="Model-X",
        manufacturer_country="USA",
        device_type="diagnostic",
        name="Test Device",
        description=None,
        is_critical=False,
        status=status,
        location_building="Building A",
        location_floor="1",
        location_room="101",
        location_department="Radiology",
        calibration_last=None,
        calibration_next=None,
        calibration_interval_days=None,
        maintenance_interval_days=None,
        notes=None,
        registered_at=datetime.now(UTC),
        registered_by="engineer-1",
        last_status_change=datetime.now(UTC),
        version=version,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    defaults.update(overrides)
    return FakeDevice(**defaults)


# ─── RegisterDevice Tests ───────────────────────────────────────────────────────


class TestRegisterDevice:
    @pytest.mark.asyncio
    async def test_register_device_success(self, device_service, mock_repository, fake_outbox):
        mock_repository.get_by_serial.return_value = None
        mock_repository.save.return_value = make_device()

        device = await device_service.register_device(
            tenant_id="tenant-1",
            serial_number="SN-001",
            name="MRI Scanner",
            device_type="imaging",
            manufacturer_name="Siemens",
            manufacturer_model="MAGNETOM",
            building="Main",
            floor="2",
            room="201",
            department="Radiology",
            registered_by="engineer-1",
        )

        assert device is not None
        mock_repository.save.assert_called_once()
        assert len(fake_outbox.appended) == 1
        assert fake_outbox.appended[0]["event_type"] == "DeviceRegistered"

    @pytest.mark.asyncio
    async def test_register_device_duplicate_serial_raises(self, device_service, mock_repository):
        mock_repository.get_by_serial.return_value = make_device()

        with pytest.raises(ValueError, match="already exists"):
            await device_service.register_device(
                tenant_id="tenant-1",
                serial_number="SN-001",
                name="MRI Scanner",
                device_type="imaging",
                manufacturer_name="Siemens",
                manufacturer_model="MAGNETOM",
                building="Main",
            )

    @pytest.mark.asyncio
    async def test_register_device_publishes_event(self, device_service, mock_repository, fake_outbox):
        mock_repository.get_by_serial.return_value = None
        mock_repository.save.return_value = make_device()

        await device_service.register_device(
            tenant_id="tenant-1",
            serial_number="SN-002",
            name="CT Scanner",
            device_type="imaging",
            manufacturer_name="GE",
            manufacturer_model="Revolution",
            building="Main",
            registered_by="engineer-2",
            correlation_id="corr-123",
        )

        assert len(fake_outbox.appended) == 1
        event = fake_outbox.appended[0]
        assert event["event_type"] == "DeviceRegistered"
        assert event["correlation_id"] == "corr-123"
        assert event["aggregate_type"] == "Device"


# ─── UpdateDevice Tests ────────────────────────────────────────────────────────


class TestUpdateDevice:
    @pytest.mark.asyncio
    async def test_update_device_success(self, device_service, mock_repository, fake_outbox):
        device = make_device()
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = make_device(version=2)

        updated = await device_service.update_device(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            name="Updated Name",
        )

        assert updated is not None
        mock_repository.update.assert_called_once()
        assert any(e["event_type"] == "DeviceUpdated" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_update_device_not_found_raises(self, device_service, mock_repository):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await device_service.update_device(
                device_id="nonexistent",
                tenant_id="tenant-1",
                expected_version=1,
                name="Updated",
            )

    @pytest.mark.asyncio
    async def test_update_device_version_mismatch_raises(self, device_service, mock_repository):
        device = make_device(version=3)
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="version mismatch"):
            await device_service.update_device(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                name="Updated",
            )


# ─── TransferDevice Tests ─────────────────────────────────────────────────────


class TestTransferDevice:
    @pytest.mark.asyncio
    async def test_transfer_device_success(self, device_service, mock_repository, fake_outbox):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = make_device(
            location_building="Building B", location_floor="3", version=2
        )

        updated = await device_service.transfer_device(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            new_building="Building B",
            new_floor="3",
            new_room="301",
            new_department="ICU",
            transfer_reason="Relocation",
            transferred_by="engineer-1",
        )

        assert updated is not None
        assert any(e["event_type"] == "DeviceTransferred" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_transfer_decommissioned_device_raises(self, device_service, mock_repository):
        device = make_device(status="decommissioned")
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="decommissioned"):
            await device_service.transfer_device(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                new_building="Building B",
            )


# ─── Maintenance Tests ─────────────────────────────────────────────────────────


class TestMaintenance:
    @pytest.mark.asyncio
    async def test_schedule_maintenance_success(self, device_service, mock_repository, fake_outbox):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device

        await device_service.schedule_maintenance(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            maintenance_type="preventive",
            scheduled_date="2026-08-01",
            technician_id="tech-1",
        )

        assert any(e["event_type"] == "MaintenanceScheduled" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_schedule_maintenance_on_decommissioned_raises(self, device_service, mock_repository):
        device = make_device(status="decommissioned")
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="decommissioned"):
            await device_service.schedule_maintenance(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                maintenance_type="preventive",
                scheduled_date="2026-08-01",
            )

    @pytest.mark.asyncio
    async def test_schedule_maintenance_while_in_maintenance_raises(self, device_service, mock_repository):
        device = make_device(status="in_maintenance")
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="already in maintenance"):
            await device_service.schedule_maintenance(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                maintenance_type="preventive",
                scheduled_date="2026-08-01",
            )

    @pytest.mark.asyncio
    async def test_start_maintenance_success(self, device_service, mock_repository, fake_outbox):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = make_device(status="in_maintenance", version=2)

        updated = await device_service.start_maintenance(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            maintenance_type="corrective",
            technician_id="tech-1",
        )

        assert updated is not None
        assert any(e["event_type"] == "MaintenanceStarted" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_start_maintenance_on_decommissioned_raises(self, device_service, mock_repository):
        device = make_device(status="decommissioned")
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="decommissioned"):
            await device_service.start_maintenance(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                maintenance_type="corrective",
                technician_id="tech-1",
            )

    @pytest.mark.asyncio
    async def test_finish_maintenance_success(self, device_service, mock_repository, fake_outbox):
        device = make_device(status="in_maintenance")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = make_device(status="active", version=2)

        next_cal = datetime(2027, 1, 1, tzinfo=UTC)
        updated = await device_service.finish_maintenance(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            completed_by="tech-1",
            next_calibration_date=next_cal,
        )

        assert updated is not None
        assert any(e["event_type"] == "MaintenanceCompleted" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_finish_maintenance_not_in_maintenance_raises(self, device_service, mock_repository):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="not in maintenance"):
            await device_service.finish_maintenance(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                completed_by="tech-1",
            )


# ─── Calibration Tests ─────────────────────────────────────────────────────────


class TestCalibrateDevice:
    @pytest.mark.asyncio
    async def test_calibrate_device_success(self, device_service, mock_repository, fake_outbox):
        device = make_device(status="calibration_due")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = make_device(status="active", version=2)

        last_cal = datetime(2026, 7, 1, tzinfo=UTC)
        next_cal = datetime(2027, 7, 1, tzinfo=UTC)

        updated = await device_service.calibrate_device(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            calibration_last=last_cal,
            calibration_next=next_cal,
            calibration_interval_days=365,
            calibrated_by="engineer-1",
        )

        assert updated is not None
        assert any(e["event_type"] == "CalibrationCompleted" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_calibrate_decommissioned_device_raises(self, device_service, mock_repository):
        device = make_device(status="decommissioned")
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="decommissioned"):
            await device_service.calibrate_device(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                calibration_last=datetime.now(UTC),
                calibration_next=datetime(2027, 1, 1, tzinfo=UTC),
                calibration_interval_days=365,
                calibrated_by="engineer-1",
            )


# ─── Out of Service Tests ─────────────────────────────────────────────────────


class TestOutOfService:
    @pytest.mark.asyncio
    async def test_take_out_of_service_success(self, device_service, mock_repository, fake_outbox):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = make_device(status="out_of_service", version=2)

        updated = await device_service.take_out_of_service(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            reason="Equipment malfunction",
            taken_by="engineer-1",
        )

        assert updated is not None
        assert any(e["event_type"] == "DeviceOutOfService" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_take_already_out_of_service_raises(self, device_service, mock_repository):
        device = make_device(status="out_of_service")
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="already out of service"):
            await device_service.take_out_of_service(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                reason="Equipment malfunction",
                taken_by="engineer-1",
            )


# ─── Return to Service Tests ──────────────────────────────────────────────────


class TestReturnToService:
    @pytest.mark.asyncio
    async def test_return_to_service_success(self, device_service, mock_repository, fake_outbox):
        future = datetime(2030, 1, 1, tzinfo=UTC)
        device = make_device(status="out_of_service", calibration_next=future)
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = make_device(status="active", version=2)

        updated = await device_service.return_to_service(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            returned_by="engineer-1",
        )

        assert updated is not None
        assert any(e["event_type"] == "DeviceReturnedToService" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_return_to_service_no_calibration_raises(self, device_service, mock_repository):
        device = make_device(status="out_of_service", calibration_next=None)
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="no calibration date"):
            await device_service.return_to_service(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                returned_by="engineer-1",
            )


# ─── Decommission Tests ───────────────────────────────────────────────────────


class TestDecommission:
    @pytest.mark.asyncio
    async def test_decommission_device_success(self, device_service, mock_repository, fake_outbox):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = make_device(status="decommissioned", version=2)

        updated = await device_service.decommission_device(
            device_id=str(device.id),
            tenant_id="tenant-1",
            expected_version=1,
            reason="End of life",
            decommissioned_by="manager-1",
        )

        assert updated is not None
        assert any(e["event_type"] == "DeviceDecommissioned" for e in fake_outbox.appended)

    @pytest.mark.asyncio
    async def test_decommission_already_decommissioned_raises(self, device_service, mock_repository):
        device = make_device(status="decommissioned")
        mock_repository.get_by_id.return_value = device

        with pytest.raises(ValueError, match="already decommissioned"):
            await device_service.decommission_device(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                reason="End of life",
                decommissioned_by="manager-1",
            )


# ─── Query Tests ──────────────────────────────────────────────────────────────


class TestDeviceQueries:
    @pytest.mark.asyncio
    async def test_get_device_returns_device(self, device_service, mock_repository):
        device = make_device()
        mock_repository.get_by_id.return_value = device

        result = await device_service.get_device(str(device.id), "tenant-1")
        assert result == device

    @pytest.mark.asyncio
    async def test_get_device_returns_none_for_missing(self, device_service, mock_repository):
        mock_repository.get_by_id.return_value = None
        result = await device_service.get_device("nonexistent", "tenant-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_devices_pagination(self, device_service, mock_repository):
        devices = [make_device() for _ in range(5)]
        mock_repository.list_by_tenant.return_value = (devices, 10)

        result, total = await device_service.list_devices(
            tenant_id="tenant-1",
            page=1,
            page_size=5,
            status="active",
        )
        assert result == devices
        assert total == 10

    @pytest.mark.asyncio
    async def test_list_devices_with_all_filters(self, device_service, mock_repository):
        devices = [make_device(device_type="imaging")]
        mock_repository.list_by_tenant.return_value = (devices, 3)

        result, total = await device_service.list_devices(
            tenant_id="tenant-1",
            page=1, page_size=10,
            device_type="imaging",
            building="Main",
            department="Radiology",
        )
        mock_repository.list_by_tenant.assert_called_once()
        assert result == devices


# ─── Delete Tests ──────────────────────────────────────────────────────────────


class TestDeleteDevice:
    @pytest.mark.asyncio
    async def test_delete_device_success(self, device_service, mock_repository):
        device = make_device()
        mock_repository.get_by_id.return_value = device
        mock_repository.delete.return_value = True

        result = await device_service.delete_device(str(device.id), "tenant-1")
        assert result is True
        mock_repository.delete.assert_called_once_with(str(device.id), "tenant-1")

    @pytest.mark.asyncio
    async def test_delete_device_not_found(self, device_service, mock_repository):
        mock_repository.get_by_id.return_value = None

        result = await device_service.delete_device("nonexistent", "tenant-1")
        assert result is False


# ─── Transfer Edge Cases ──────────────────────────────────────────────────────


class TestTransferEdgeCases:
    @pytest.mark.asyncio
    async def test_transfer_concurrent_modification(self, device_service, mock_repository):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = None  # Version mismatch

        with pytest.raises(ValueError, match="Concurrent modification"):
            await device_service.transfer_device(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                new_building="Building B",
            )

    @pytest.mark.asyncio
    async def test_transfer_device_not_found(self, device_service, mock_repository):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await device_service.transfer_device(
                device_id="nonexistent",
                tenant_id="tenant-1",
                expected_version=1,
                new_building="Building B",
            )


# ─── Calibration Edge Cases ──────────────────────────────────────────────────


class TestCalibrationEdgeCases:
    @pytest.mark.asyncio
    async def test_calibrate_concurrent_modification(self, device_service, mock_repository):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = None

        with pytest.raises(ValueError, match="Concurrent modification"):
            await device_service.calibrate_device(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                calibration_last=datetime.now(UTC),
                calibration_next=datetime(2027, 1, 1, tzinfo=UTC),
                calibration_interval_days=365,
                calibrated_by="engineer-1",
            )


# ─── Start Maintenance Edge Cases ─────────────────────────────────────────────


class TestStartMaintenanceEdgeCases:
    @pytest.mark.asyncio
    async def test_start_maintenance_concurrent_modification(self, device_service, mock_repository):
        device = make_device(status="active")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = None

        with pytest.raises(ValueError, match="Concurrent modification"):
            await device_service.start_maintenance(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                maintenance_type="corrective",
                technician_id="tech-1",
            )


# ─── Finish Maintenance Edge Cases ────────────────────────────────────────────


class TestFinishMaintenanceEdgeCases:
    @pytest.mark.asyncio
    async def test_finish_maintenance_concurrent_modification(self, device_service, mock_repository):
        device = make_device(status="in_maintenance")
        mock_repository.get_by_id.return_value = device
        mock_repository.update.return_value = None

        with pytest.raises(ValueError, match="Concurrent modification"):
            await device_service.finish_maintenance(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                completed_by="tech-1",
            )


# ─── Return to Service Edge Cases ─────────────────────────────────────────────


class TestReturnToServiceEdgeCases:
    @pytest.mark.asyncio
    async def test_return_to_service_device_not_found(self, device_service, mock_repository):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await device_service.return_to_service(
                device_id="nonexistent",
                tenant_id="tenant-1",
                expected_version=1,
                returned_by="engineer-1",
            )


# ─── Update Device Edge Cases ──────────────────────────────────────────────────


class TestUpdateDeviceEdgeCases:
    @pytest.mark.asyncio
    async def test_update_duplicate_serial_raises(self, device_service, mock_repository):
        device = make_device(serial="SN-OLD")
        existing = make_device(serial="SN-NEW")
        mock_repository.get_by_id.return_value = device
        mock_repository.get_by_serial.return_value = existing

        with pytest.raises(ValueError, match="already in use"):
            await device_service.update_device(
                device_id=str(device.id),
                tenant_id="tenant-1",
                expected_version=1,
                serial_number="SN-NEW",
            )

