"""Tests for Device aggregate."""

from __future__ import annotations

import pytest

from core.device.domain import (
    CalibrationInfo,
    Device,
    DeviceStatus,
    DeviceType,
    LocationInfo,
    ManufacturerInfo,
    SerialNumber,
)
from core.shared import DeviceId, EngineerId, TenantId


class TestDevice:
    """Tests for Device aggregate."""

    @pytest.fixture
    def tenant_id(self) -> TenantId:
        return TenantId(value="tenant_001")

    @pytest.fixture
    def device_id(self) -> DeviceId:
        return DeviceId.generate()

    @pytest.fixture
    def engineer_id(self) -> EngineerId:
        return EngineerId(value="engineer_001")

    @pytest.fixture
    def manufacturer(self) -> ManufacturerInfo:
        return ManufacturerInfo(
            name="MedTech Corp",
            model="MRI-3000",
            manufacturing_date="2024-01-15",
            country_of_origin="USA",
        )

    @pytest.fixture
    def serial_number(self) -> SerialNumber:
        return SerialNumber.from_string("SN-2024-001")

    @pytest.fixture
    def device_type(self) -> DeviceType:
        return DeviceType.diagnostic()

    @pytest.fixture
    def location(self) -> LocationInfo:
        return LocationInfo(
            building="Main",
            floor="2",
            room="201",
            department="Radiology",
        )

    def test_create_device(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
    ):
        """Test creating a new device."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )

        assert device.tenant_id == tenant_id
        assert device.serial_number == serial_number
        assert device.name == "MRI Scanner"
        assert device.status == DeviceStatus.registered()
        assert device.version == 1
        assert device.has_pending_events()

    def test_device_publishes_event_on_creation(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
    ):
        """Test that device publishes event on creation."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )

        events = device.pop_events()
        assert len(events) == 1
        assert events[0].event_type == "DeviceRegistered"

    def test_activate_device(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
        engineer_id,
    ):
        """Test activating a device."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )
        device.pop_events()

        device.activate(activated_by=engineer_id, expected_version=1)

        assert device.status == DeviceStatus.active()
        assert device.version == 2

    def test_cannot_activate_decommissioned_device(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
        engineer_id,
    ):
        """Test that decommissioned devices cannot be activated."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )
        device.pop_events()

        device.decommission(reason="End of life", decommissioned_by=engineer_id)

        with pytest.raises(Exception):
            device.activate(activated_by=engineer_id, expected_version=2)

    def test_take_out_of_service(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
        engineer_id,
    ):
        """Test taking a device out of service."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )
        device.pop_events()

        device.activate(activated_by=engineer_id, expected_version=1)
        device.take_out_of_service(reason="Scheduled maintenance", taken_by=engineer_id, expected_version=2)

        assert device.status == DeviceStatus.out_of_service()
        assert "Out of service: Scheduled maintenance" in (device.notes or "")

    def test_start_maintenance(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
        engineer_id,
    ):
        """Test starting maintenance on device."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )
        device.pop_events()

        device.activate(activated_by=engineer_id, expected_version=1)
        device.start_maintenance(maintenance_type="Preventive", engineer_id=engineer_id, expected_version=2)

        assert device.status == DeviceStatus.in_maintenance()

    def test_complete_maintenance(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
        engineer_id,
    ):
        """Test completing maintenance."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )
        device.pop_events()

        device.activate(activated_by=engineer_id, expected_version=1)
        device.start_maintenance(maintenance_type="Preventive", engineer_id=engineer_id, expected_version=2)
        device.complete_maintenance(completed_by=engineer_id, expected_version=3)

        assert device.status == DeviceStatus.active()

    def test_decommission_device(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
        engineer_id,
    ):
        """Test decommissioning a device."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )
        device.pop_events()

        device.decommission(reason="End of life", decommissioned_by=engineer_id)

        assert device.status == DeviceStatus.decommissioned()
        assert "Decommissioned: End of life" in (device.notes or "")

    def test_relocate_device(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
        engineer_id,
    ):
        """Test relocating a device."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )
        device.pop_events()

        new_location = LocationInfo(
            building="East Wing",
            floor="3",
            room="301",
            department="Emergency",
        )
        device.relocate(new_location=new_location, relocated_by=engineer_id)

        assert device.location == new_location
        assert device.has_pending_events()

    def test_is_operational(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        device_type,
        location,
        engineer_id,
    ):
        """Test operational status check."""
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=device_type,
            name="MRI Scanner",
            location=location,
        )

        # Registered is not operational
        assert not device.is_operational()

        # Active is operational
        device.pop_events()
        device.activate(activated_by=engineer_id, expected_version=1)
        assert device.is_operational()

        # Maintenance is not operational
        device.start_maintenance(maintenance_type="Repair", engineer_id=engineer_id, expected_version=2)
        assert not device.is_operational()

    def test_high_risk_device(
        self,
        device_id,
        tenant_id,
        serial_number,
        manufacturer,
        location,
    ):
        """Test high risk device classification."""
        high_risk_type = DeviceType(
            value="life_support",
            risk_classification="class_d",
        )
        device = Device(
            id=device_id,
            tenant_id=tenant_id,
            serial_number=serial_number,
            manufacturer=manufacturer,
            device_type=high_risk_type,
            name="Ventilator",
            location=location,
        )

        assert device.is_high_risk_device()


class TestDeviceValueObjects:
    """Tests for Device value objects."""

    def test_device_status_factory_methods(self):
        """Test status factory methods."""
        assert DeviceStatus.registered().value == "registered"
        assert DeviceStatus.active().value == "active"
        assert DeviceStatus.in_maintenance().value == "in_maintenance"

    def test_device_status_is_operational(self):
        """Test operational checks."""
        assert DeviceStatus.active().is_operational()
        assert DeviceStatus.calibration_due().is_operational()
        assert not DeviceStatus.in_maintenance().is_operational()

    def test_device_status_requires_attention(self):
        """Test attention required checks."""
        assert DeviceStatus.in_maintenance().requires_attention()
        assert DeviceStatus.calibration_due().requires_attention()
        assert DeviceStatus.out_of_service().requires_attention()
        assert not DeviceStatus.active().requires_attention()

    def test_device_type_factory_methods(self):
        """Test device type factory methods."""
        assert DeviceType.diagnostic().value == "diagnostic"
        assert DeviceType.life_support().value == "life_support"
        assert DeviceType.life_support().is_high_risk()

    def test_serial_number_validation(self):
        """Test serial number validation."""
        serial = SerialNumber.from_string("  ABC-123  ")
        assert serial.value == "ABC-123"

        with pytest.raises(ValueError):
            SerialNumber(value="")

    def test_location_info(self):
        """Test location info."""
        location = LocationInfo.from_room("201", "Radiology")
        assert location.building == "Main"
        assert location.room == "201"
        assert "Floor" in location.full_address()
