"""Biomedical Device Platform Engine for EREN OS.

Manages medical device integration, connections, and data streaming.
"""

from __future__ import annotations

import asyncio
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from core.PHASE_1.infrastructure.biomedical.device_platform.types import (
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
    DriverType,
    SimulationConfig,
)


class DeviceDriver:
    """Base class for device drivers."""

    def __init__(self, device: DeviceContract, config: DriverConfig):
        """Initialize driver."""
        self.device = device
        self.config = config
        self._connected = False

    async def connect(self) -> bool:
        """Connect to device."""
        raise NotImplementedError

    async def disconnect(self) -> None:
        """Disconnect from device."""
        raise NotImplementedError

    async def read(self) -> DeviceReading | None:
        """Read a single value."""
        raise NotImplementedError

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected


class SerialDriver(DeviceDriver):
    """Serial communication driver."""

    def __init__(self, device: DeviceContract, config: DriverConfig):
        super().__init__(device, config)
        self._serial = None

    async def connect(self) -> bool:
        """Connect via serial."""
        try:
            # In real implementation, use pyserial
            self._connected = True
            return True
        except Exception:
            return False

    async def disconnect(self) -> None:
        """Disconnect."""
        self._connected = False

    async def read(self) -> DeviceReading | None:
        """Read from serial."""
        if not self._connected:
            return None
        return DeviceReading(
            device_id=self.device.device_id,
            parameter="sample",
            value=0.0,
            unit="",
        )


class TCPDriver(DeviceDriver):
    """TCP/IP driver."""

    def __init__(self, device: DeviceContract, config: DriverConfig):
        super().__init__(device, config)
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def connect(self) -> bool:
        """Connect via TCP."""
        try:
            self._reader, self._writer = await asyncio.open_connection(
                self.config.host, self.config.port
            )
            self._connected = True
            return True
        except Exception:
            return False

    async def disconnect(self) -> None:
        """Disconnect."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._connected = False

    async def read(self) -> DeviceReading | None:
        """Read from TCP."""
        if not self._connected or not self._reader:
            return None
        try:
            data = await asyncio.wait_for(
                self._reader.readline(),
                timeout=self.config.timeout_seconds
            )
            return self._parse_data(data.decode())
        except asyncio.TimeoutError:
            return None

    def _parse_data(self, data: str) -> DeviceReading:
        """Parse device data."""
        return DeviceReading(
            device_id=self.device.device_id,
            parameter="sample",
            value=float(data.strip()) if data.strip() else 0.0,
            unit="",
        )


class MockDriver(DeviceDriver):
    """Mock driver for testing."""

    def __init__(self, device: DeviceContract, config: DriverConfig):
        super().__init__(device, config)
        self._readings = 0

    async def connect(self) -> bool:
        """Mock connect."""
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """Mock disconnect."""
        self._connected = False

    async def read(self) -> DeviceReading | None:
        """Generate mock reading."""
        self._readings += 1
        return DeviceReading(
            device_id=self.device.device_id,
            timestamp=datetime.now(UTC),
            parameter="mock_value",
            value=float(self._readings % 100),
            unit="mV",
            quality="good",
        )


class DeviceManager:
    """Manager for medical devices."""

    def __init__(self):
        """Initialize device manager."""
        self._devices: dict[str, DeviceContract] = {}
        self._drivers: dict[str, DeviceDriver] = {}
        self._connections: dict[str, ConnectionInfo] = {}
        self._health: dict[str, DeviceHealth] = {}
        self._alarm_callbacks: list[Callable] = []
        self._reading_callbacks: list[Callable] = []
        self._lock = threading.RLock()
        self._simulation_config = SimulationConfig()

    def register_device(self, device: DeviceContract) -> None:
        """Register a device."""
        with self._lock:
            self._devices[device.device_id] = device
            self._connections[device.device_id] = ConnectionInfo(device_id=device.device_id)
            self._health[device.device_id] = DeviceHealth(device_id=device.device_id)

    def get_device(self, device_id: str) -> DeviceContract | None:
        """Get device contract."""
        return self._devices.get(device_id)

    def list_devices(self, category: DeviceCategory | None = None) -> list[DeviceContract]:
        """List all devices."""
        with self._lock:
            if category:
                return [d for d in self._devices.values() if d.category == category]
            return list(self._devices.values())

    async def connect_device(self, device_id: str) -> bool:
        """Connect to a device."""
        device = self._devices.get(device_id)
        if not device:
            return False

        # Create driver based on device protocol
        config = DriverConfig(driver_type=DriverType.TCP if device.connection_type == "tcp" else DriverType.SERIAL)

        if config.driver_type == DriverType.SERIAL:
            driver = SerialDriver(device, config)
        elif config.driver_type == DriverType.TCP:
            driver = TCPDriver(device, config)
        else:
            driver = MockDriver(device, config)

        # Update connection state
        self._connections[device_id].state = ConnectionState.CONNECTING

        try:
            success = await driver.connect()
            if success:
                self._drivers[device_id] = driver
                self._connections[device_id].state = ConnectionState.CONNECTED
                self._connections[device_id].last_connected = datetime.now(UTC)
                return True
            else:
                self._connections[device_id].state = ConnectionState.FAILED
                return False
        except Exception as e:
            self._connections[device_id].state = ConnectionState.FAILED
            self._connections[device_id].last_error = str(e)
            return False

    async def disconnect_device(self, device_id: str) -> None:
        """Disconnect from a device."""
        driver = self._drivers.get(device_id)
        if driver:
            await driver.disconnect()
            del self._drivers[device_id]

        if device_id in self._connections:
            self._connections[device_id].state = ConnectionState.DISCONNECTED

    async def read_device(self, device_id: str) -> DeviceReading | None:
        """Read from device."""
        driver = self._drivers.get(device_id)
        if not driver or not driver.is_connected():
            return None

        reading = await driver.read()
        if reading:
            for callback in self._reading_callbacks:
                try:
                    callback(reading)
                except Exception:
                    pass

        return reading

    def on_reading(self, callback: Callable) -> None:
        """Register reading callback."""
        self._reading_callbacks.append(callback)

    def on_alarm(self, callback: Callable) -> None:
        """Register alarm callback."""
        self._alarm_callbacks.append(callback)

    def get_health(self, device_id: str) -> DeviceHealth | None:
        """Get device health."""
        return self._health.get(device_id)

    def get_connection_state(self, device_id: str) -> ConnectionInfo | None:
        """Get connection state."""
        return self._connections.get(device_id)


# =============================================================================
# Singleton
# =============================================================================

_global_manager: DeviceManager | None = None
_manager_lock = threading.Lock()


def get_device_manager() -> DeviceManager:
    """Get global device manager."""
    global _global_manager
    with _manager_lock:
        if _global_manager is None:
            _global_manager = DeviceManager()
        return _global_manager


def reset_device_manager() -> None:
    """Reset global manager."""
    global _global_manager
    with _manager_lock:
        _global_manager = None
