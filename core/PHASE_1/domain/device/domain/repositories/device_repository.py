"""Repository interface for Device."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import DeviceId, Result, TenantId

from ..entities import Device

if TYPE_CHECKING:
    pass


class DeviceRepository(ABC):
    """Repository interface for Device aggregate."""

    @abstractmethod
    async def save(self, device: Device) -> Result[Device, str]:
        """Save a device."""

    @abstractmethod
    async def get_by_id(self, device_id: DeviceId) -> Result[Device | None, str]:
        """Get a device by ID."""

    @abstractmethod
    async def get_by_serial(
        self,
        serial_number: str,
        tenant_id: TenantId,
    ) -> Result[Device | None, str]:
        """Get a device by serial number."""

    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[Device], str]:
        """Get all devices for a tenant."""

    @abstractmethod
    async def get_by_status(
        self,
        tenant_id: TenantId,
        status: str,
        limit: int = 50,
    ) -> Result[list[Device], str]:
        """Get devices by status."""

    @abstractmethod
    async def get_by_location(
        self,
        tenant_id: TenantId,
        building: str,
        floor: str | None = None,
        department: str | None = None,
    ) -> Result[list[Device], str]:
        """Get devices by location."""

    @abstractmethod
    async def get_critical_devices(
        self,
        tenant_id: TenantId,
    ) -> Result[list[Device], str]:
        """Get all critical devices."""

    @abstractmethod
    async def get_needing_maintenance(
        self,
        tenant_id: TenantId,
    ) -> Result[list[Device], str]:
        """Get devices that need maintenance."""

    @abstractmethod
    async def get_calibration_due(
        self,
        tenant_id: TenantId,
        days_threshold: int = 30,
    ) -> Result[list[Device], str]:
        """Get devices with calibration due."""

    @abstractmethod
    async def delete(self, device_id: DeviceId) -> Result[bool, str]:
        """Delete a device (soft delete)."""
