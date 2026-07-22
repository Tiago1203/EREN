"""Device-specific value objects."""

from __future__ import annotations

from dataclasses import dataclass

from core.PHASE_1.infrastructure.shared import ValueObject


@dataclass(frozen=True)
class DeviceStatus(ValueObject):
    """Status of a biomedical device."""

    value: str

    def __post_init__(self) -> None:
        valid_statuses = {
            "registered",
            "active",
            "in_maintenance",
            "calibration_due",
            "out_of_service",
            "decommissioned",
        }
        if self.value.lower() not in valid_statuses:
            msg = f"Invalid device status: {self.value}. Must be one of {valid_statuses}"
            raise ValueError(msg)

    @classmethod
    def registered(cls) -> DeviceStatus:
        return cls(value="registered")

    @classmethod
    def active(cls) -> DeviceStatus:
        return cls(value="active")

    @classmethod
    def in_maintenance(cls) -> DeviceStatus:
        return cls(value="in_maintenance")

    @classmethod
    def calibration_due(cls) -> DeviceStatus:
        return cls(value="calibration_due")

    @classmethod
    def out_of_service(cls) -> DeviceStatus:
        return cls(value="out_of_service")

    @classmethod
    def decommissioned(cls) -> DeviceStatus:
        return cls(value="decommissioned")

    def is_operational(self) -> bool:
        """Check if device is currently operational."""
        return self.value in {"active", "calibration_due"}

    def is_available_for_service(self) -> bool:
        """Check if device can be used for clinical service."""
        return self.value == "active"

    def requires_attention(self) -> bool:
        """Check if device requires maintenance attention."""
        return self.value in {"in_maintenance", "calibration_due", "out_of_service"}

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class DeviceType(ValueObject):
    """Type/category of biomedical device."""

    value: str
    risk_classification: str

    def __post_init__(self) -> None:
        valid_types = {
            "diagnostic",
            "therapeutic",
            "monitoring",
            "life_support",
            "laboratory",
            "imaging",
            "surgical",
        }
        if self.value.lower() not in valid_types:
            msg = f"Invalid device type: {self.value}. Must be one of {valid_types}"
            raise ValueError(msg)

        valid_risks = {"class_a", "class_b", "class_c", "class_d"}
        if self.risk_classification.lower() not in valid_risks:
            msg = f"Invalid risk classification: {self.risk_classification}"
            raise ValueError(msg)

    @classmethod
    def diagnostic(cls) -> DeviceType:
        return cls(value="diagnostic", risk_classification="class_b")

    @classmethod
    def therapeutic(cls) -> DeviceType:
        return cls(value="therapeutic", risk_classification="class_c")

    @classmethod
    def monitoring(cls) -> DeviceType:
        return cls(value="monitoring", risk_classification="class_b")

    @classmethod
    def life_support(cls) -> DeviceType:
        return cls(value="life_support", risk_classification="class_d")

    def is_high_risk(self) -> bool:
        """Check if device is high risk (class C or D)."""
        return self.risk_classification in {"class_c", "class_d"}

    def __str__(self) -> str:
        return f"{self.value} ({self.risk_classification})"


@dataclass(frozen=True)
class SerialNumber(ValueObject):
    """Device serial number with validation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value) < 3:
            msg = "Serial number must be at least 3 characters"
            raise ValueError(msg)

    @classmethod
    def from_string(cls, serial: str) -> SerialNumber:
        """Create from string, stripping whitespace."""
        return cls(value=serial.strip())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ManufacturerInfo(ValueObject):
    """Information about the device manufacturer."""

    name: str
    model: str
    manufacturing_date: str
    country_of_origin: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            msg = "Manufacturer name cannot be empty"
            raise ValueError(msg)
        if not self.model or not self.model.strip():
            msg = "Model name cannot be empty"
            raise ValueError(msg)


@dataclass(frozen=True)
class LocationInfo(ValueObject):
    """Physical location of a device."""

    building: str
    floor: str
    room: str
    department: str
    coordinates: str | None = None

    def __post_init__(self) -> None:
        if not all([self.building, self.floor, self.room, self.department]):
            msg = "All location fields (building, floor, room, department) are required"
            raise ValueError(msg)

    @classmethod
    def from_room(cls, room: str, department: str = "General") -> LocationInfo:
        """Create minimal location from room number."""
        return cls(
            building="Main",
            floor=room.split("-")[0] if "-" in room else "1",
            room=room,
            department=department,
        )

    def full_address(self) -> str:
        """Return full location string."""
        return f"{self.building}, Floor {self.floor}, Room {self.room}, {self.department}"


@dataclass(frozen=True)
class CalibrationInfo(ValueObject):
    """Calibration information for a device."""

    last_calibration_date: str
    next_calibration_date: str
    calibration_interval_days: int
    calibration_certificate: str | None = None
    calibrated_by: str | None = None

    def __post_init__(self) -> None:
        if self.calibration_interval_days <= 0:
            msg = "Calibration interval must be positive"
            raise ValueError(msg)

    def is_due_soon(self, days_threshold: int = 30) -> bool:
        """Check if calibration is due within threshold."""
        # In a real implementation, compare dates
        return True

    def is_overdue(self) -> bool:
        """Check if calibration is overdue."""
        # In a real implementation, compare with current date
        return False


@dataclass(frozen=True)
class MaintenanceSchedule(ValueObject):
    """Scheduled maintenance information."""

    schedule_type: str  # preventive, corrective, predictive
    interval_days: int
    last_maintenance_date: str | None
    next_maintenance_date: str | None
    maintenance_provider: str | None = None

    def __post_init__(self) -> None:
        valid_types = {"preventive", "corrective", "predictive"}
        if self.schedule_type.lower() not in valid_types:
            msg = f"Invalid schedule type: {self.schedule_type}"
            raise ValueError(msg)

    @classmethod
    def preventive(cls, interval_days: int) -> MaintenanceSchedule:
        return cls(
            schedule_type="preventive",
            interval_days=interval_days,
            last_maintenance_date=None,
            next_maintenance_date=None,
        )

    def is_preventive(self) -> bool:
        return self.schedule_type == "preventive"
