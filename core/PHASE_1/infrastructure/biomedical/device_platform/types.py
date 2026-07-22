"""Biomedical Device Platform Types for EREN OS.

Type definitions for medical device integration, protocols, and drivers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Device Types
# =============================================================================


class DeviceCategory(str, Enum):
    """Categories of medical devices."""

    MONITOR = "monitor"  # Multiparameter monitor
    VENTILATOR = "ventilator"
    INFUSION_PUMP = "infusion_pump"
    ECG = "ecg"
    DEFIBRILLATOR = "defibrillator"
    IMAGING = "imaging"  # X-Ray, CT, MRI, Ultrasound
    LABORATORY = "laboratory"
    Incubator = "incubator"
    FETAL_MONITOR = "fetal_monitor"
    ELECTROSURGERY = "electrosurgery"
    ANESTHESIA = "anesthesia"


class DeviceStatus(str, Enum):
    """Device status."""

    ONLINE = "online"
    OFFLINE = "offline"
    STANDBY = "standby"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    CALIBRATING = "calibrating"


# =============================================================================
# Device Contract
# =============================================================================


@dataclass
class DeviceCapability:
    """A capability of a device."""

    name: str
    description: str = ""
    data_type: str = ""  # waveform, numeric, alarm
    unit: str = ""
    sampling_rate: float = 0.0  # Hz


@dataclass
class DeviceContract:
    """Contract for device integration."""

    device_id: str
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    firmware_version: str = ""
    category: DeviceCategory = DeviceCategory.MONITOR
    capabilities: list[DeviceCapability] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)  # HL7, FHIR, DICOM, etc.
    connection_type: str = ""  # serial, tcp, usb, bluetooth, wifi
    port: int = 0
    ip_address: str = ""


# =============================================================================
# Device Driver
# =============================================================================


class DriverType(str, Enum):
    """Types of device drivers."""

    SERIAL = "serial"
    TCP = "tcp"
    USB = "usb"
    BLUETOOTH = "bluetooth"
    HL7 = "hl7"
    FHIR = "fhir"
    DICOM = "dicom"


@dataclass
class DriverConfig:
    """Configuration for device driver."""

    driver_type: DriverType = DriverType.SERIAL
    host: str = "localhost"
    port: int = 0
    baud_rate: int = 9600
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = "none"
    timeout_seconds: float = 30.0
    retry_count: int = 3


# =============================================================================
# Device Data
# =============================================================================


@dataclass
class DeviceReading:
    """A reading from a device."""

    device_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    parameter: str = ""
    value: float = 0.0
    unit: str = ""
    quality: str = "good"  # good, fair, poor, invalid


@dataclass
class DeviceWaveform:
    """A waveform from a device."""

    device_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    waveform_type: str = ""  # ECG, respiration, etc.
    data: list[float] = field(default_factory=list)
    sample_rate: float = 0.0
    duration_ms: int = 0


@dataclass
class DeviceAlarm:
    """An alarm from a device."""

    alarm_id: str
    device_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    priority: str = "low"  # low, medium, high, critical
    code: str = ""
    message: str = ""
    acknowledged: bool = False
    acknowledged_by: str = ""
    acknowledged_at: datetime | None = None


# =============================================================================
# Connection Manager
# =============================================================================


class ConnectionState(str, Enum):
    """Connection state."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class ConnectionInfo:
    """Information about device connection."""

    device_id: str
    state: ConnectionState = ConnectionState.DISCONNECTED
    last_connected: datetime | None = None
    last_error: str = ""
    reconnect_attempts: int = 0


# =============================================================================
# Health Monitor
# =============================================================================


@dataclass
class DeviceHealth:
    """Health status of a device."""

    device_id: str
    is_healthy: bool = True
    status: DeviceStatus = DeviceStatus.ONLINE
    battery_level: int = 100  # %
    signal_strength: int = 0  # dBm
    firmware_up_to_date: bool = True
    last_calibration: datetime | None = None
    next_maintenance: datetime | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# =============================================================================
# Simulation
# =============================================================================


@dataclass
class SimulationConfig:
    """Configuration for device simulation."""

    enabled: bool = False
    waveform_type: str = "ecg"
    heart_rate: int = 72
    respiratory_rate: int = 16
    spo2: int = 98
    blood_pressure: tuple[int, int] = (120, 80)
    temperature: float = 36.5
