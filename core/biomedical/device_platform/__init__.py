"""Biomedical Device Platform for EREN OS.

PR-062: Biomedical Device Platform

Provides medical device integration with support for HL7, FHIR, DICOM,
and various connection protocols.
"""

from __future__ import annotations

from core.biomedical.device_platform.engine import (
    DeviceDriver,
    DeviceManager,
    DriverType,
    MockDriver,
    SerialDriver,
    TCPDriver,
    get_device_manager,
    reset_device_manager,
)
from core.biomedical.device_platform.types import (
    ConnectionInfo,
    ConnectionState,
    DeviceAlarm,
    DeviceCapability,
    DeviceCategory,
    DeviceContract,
    DeviceHealth,
    DeviceReading,
    DeviceStatus,
    DeviceWaveform,
    DriverConfig,
    SimulationConfig,
)

__all__ = [
    # Engine
    "DeviceManager",
    "DeviceDriver",
    "SerialDriver",
    "TCPDriver",
    "MockDriver",
    "get_device_manager",
    "reset_device_manager",
    # Types
    "DeviceCategory",
    "DeviceStatus",
    "DeviceContract",
    "DeviceCapability",
    "DriverType",
    "DriverConfig",
    "DeviceReading",
    "DeviceWaveform",
    "DeviceAlarm",
    "ConnectionState",
    "ConnectionInfo",
    "DeviceHealth",
    "SimulationConfig",
]
