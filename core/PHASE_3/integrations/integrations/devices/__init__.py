"""Medical Device Adapters - Philips, GE, Dräger, Mindray."""
from dataclasses import dataclass
from enum import Enum

from core.PHASE_3.integrations.devices.base import (
    DeviceAlarm,
    DeviceInfo,
    DeviceReading,
    DeviceStatus,
    DeviceAdapterRegistry,
    MedicalDeviceAdapter,
    get_adapter_registry,
)
from core.PHASE_3.integrations.devices.philips import PhilipsIntelliVueAdapter
from core.PHASE_3.integrations.devices.ge import GEHealthcareAdapter
from core.PHASE_3.integrations.devices.draeger import DraegerMedicalAdapter
from core.PHASE_3.integrations.devices.mindray import MindrayAdapter


class DeviceVendor(str, Enum):
    PHILIPS = "philips"
    GE = "ge"
    DRAGER = "drager"
    MINDRAY = "mindray"


@dataclass
class DeviceTelemetry:
    """Device telemetry data."""
    device_id: str
    vendor: DeviceVendor
    timestamp: str
    metrics: dict


@dataclass
class DeviceAlert:
    """Device alert notification."""
    device_id: str
    severity: str
    code: str
    description: str


@dataclass
class DeviceConfig:
    """Configuration for device connection."""
    vendor: DeviceVendor
    host: str
    port: int
    username: str | None = None
    password: str | None = None


__all__ = [
    "MedicalDeviceAdapter",
    "DeviceAdapterRegistry",
    "DeviceInfo",
    "DeviceReading",
    "DeviceAlarm",
    "DeviceStatus",
    "DeviceVendor",
    "DeviceTelemetry",
    "DeviceAlert",
    "DeviceConfig",
    "PhilipsIntelliVueAdapter",
    "GEHealthcareAdapter",
    "DraegerMedicalAdapter",
    "MindrayAdapter",
    "get_adapter_registry",
]
