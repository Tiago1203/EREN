"""Medical Device Adapters - Philips, GE, Dräger, Mindray."""
from dataclasses import dataclass
from enum import Enum


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
