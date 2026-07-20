"""Medical Device Adapters - Base Interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    STANDBY = "standby"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class DeviceReading:
    """Represents a device measurement reading."""
    timestamp: datetime
    parameter: str
    value: float | str
    unit: str | None = None
    alarm: bool = False
    alarm_priority: str | None = None


@dataclass
class DeviceAlarm:
    """Represents a device alarm."""
    alarm_id: str
    timestamp: datetime
    priority: str
    parameter: str
    message: str
    acknowledged: bool = False


@dataclass
class DeviceInfo:
    """Basic device information."""
    device_id: str
    model: str
    manufacturer: str
    serial_number: str
    status: DeviceStatus
    software_version: str | None = None
    last_maintenance: datetime | None = None


class MedicalDeviceAdapter(ABC):
    """
    Abstract base class for medical device adapters.
    
    All device-specific adapters must implement this interface.
    """

    @property
    @abstractmethod
    def manufacturer(self) -> str:
        """Return device manufacturer name."""
        pass

    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        """Return list of supported device models."""
        pass

    @abstractmethod
    async def connect(self, host: str, port: int) -> bool:
        """
        Establish connection to the device.
        
        Args:
            host: Device IP address
            port: Device port
            
        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the device."""
        pass

    @abstractmethod
    async def get_device_info(self) -> DeviceInfo:
        """Retrieve device information."""
        pass

    @abstractmethod
    async def get_status(self) -> DeviceStatus:
        """Get current device status."""
        pass

    @abstractmethod
    async def read_parameters(self) -> list[DeviceReading]:
        """Read current parameter values."""
        pass

    @abstractmethod
    async def get_alarms(self) -> list[DeviceAlarm]:
        """Get active alarms."""
        pass

    @abstractmethod
    async def acknowledge_alarm(self, alarm_id: str) -> bool:
        """
        Acknowledge an alarm.
        
        Args:
            alarm_id: Alarm identifier
            
        Returns:
            True if acknowledgment successful
        """
        pass

    @abstractmethod
    async def send_command(self, command: str, parameters: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Send a command to the device.
        
        Args:
            command: Command identifier
            parameters: Optional command parameters
            
        Returns:
            Command response
        """
        pass


class DeviceAdapterRegistry:
    """
    Registry for medical device adapters.
    
    Allows lookup of adapters by manufacturer or model.
    """

    def __init__(self):
        self._adapters: dict[str, type[MedicalDeviceAdapter]] = {}

    def register(
        self,
        manufacturer: str,
        adapter_class: type[MedicalDeviceAdapter],
    ) -> None:
        """Register a device adapter."""
        self._adapters[manufacturer.lower()] = adapter_class

    def get_adapter(self, manufacturer: str) -> type[MedicalDeviceAdapter] | None:
        """Get adapter class for a manufacturer."""
        return self._adapters.get(manufacturer.lower())

    def list_manufacturers(self) -> list[str]:
        """List all registered manufacturers."""
        return list(self._adapters.keys())


# Global registry instance
_registry: DeviceAdapterRegistry | None = None


def get_adapter_registry() -> DeviceAdapterRegistry:
    """Get the global device adapter registry."""
    global _registry
    if _registry is None:
        _registry = DeviceAdapterRegistry()
        _register_default_adapters(_registry)
    return _registry


def _register_default_adapters(registry: DeviceAdapterRegistry) -> None:
    """Register built-in device adapters."""
    from core.integrations.devices.philips import PhilipsIntelliVueAdapter
    from core.integrations.devices.ge import GEHealthcareAdapter
    from core.integrations.devices.draeger import DraegerMedicalAdapter
    from core.integrations.devices.mindray import MindrayAdapter

    registry.register("Philips", PhilipsIntelliVueAdapter)
    registry.register("GE Healthcare", GEHealthcareAdapter)
    registry.register("Dräger", DraegerMedicalAdapter)
    registry.register("Drager", DraegerMedicalAdapter)
    registry.register("Mindray", MindrayAdapter)
