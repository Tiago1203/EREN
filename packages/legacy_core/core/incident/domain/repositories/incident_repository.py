"""Repository interface for Engineering Incident."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.shared import DeviceId, EngineerId, IncidentId, Result, TenantId

from ..entities import EngineeringIncident

if TYPE_CHECKING:
    pass


class IncidentRepository(ABC):
    """Repository interface for EngineeringIncident aggregate.

    Following the Repository pattern from DDD, this interface
    abstracts the persistence layer.
    """

    @abstractmethod
    async def save(self, incident: EngineeringIncident) -> Result[EngineeringIncident, str]:
        """Save an incident to the repository."""

    @abstractmethod
    async def get_by_id(self, incident_id: IncidentId) -> Result[EngineeringIncident | None, str]:
        """Get an incident by its ID."""

    @abstractmethod
    async def get_by_device(
        self,
        device_id: DeviceId,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        """Get all incidents for a device."""

    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[EngineeringIncident], str]:
        """Get all incidents for a tenant."""

    @abstractmethod
    async def get_open_incidents(
        self,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        """Get all open incidents for a tenant."""

    @abstractmethod
    async def get_by_engineer(
        self,
        engineer_id: EngineerId,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        """Get all incidents assigned to an engineer."""

    @abstractmethod
    async def delete(self, incident_id: IncidentId) -> Result[bool, str]:
        """Delete an incident (soft delete)."""
