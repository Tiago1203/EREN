"""Repository interface for Bed aggregate."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.shared import BedId, Result, TenantId

from ..entities.bed import Bed, BedStatus

if TYPE_CHECKING:
    pass


class BedRepository(ABC):
    """Repository interface for Bed aggregate."""

    @abstractmethod
    async def save(self, bed: Bed) -> Result[Bed, str]:
        """Save a bed."""

    @abstractmethod
    async def get_by_id(self, bed_id: BedId) -> Result[Bed | None, str]:
        """Get a bed by ID."""

    @abstractmethod
    async def get_by_room(
        self,
        tenant_id: TenantId,
        room_id: str,
    ) -> Result[list[Bed], str]:
        """Get all beds in a room."""

    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[Bed], str]:
        """Get all beds for a tenant."""

    @abstractmethod
    async def get_available_beds(
        self,
        tenant_id: TenantId,
        campus_id: str | None = None,
        bed_type: str | None = None,
        limit: int = 50,
    ) -> Result[list[Bed], str]:
        """Get available beds (capacity query)."""

    @abstractmethod
    async def get_by_status(
        self,
        tenant_id: TenantId,
        status: BedStatus,
        limit: int = 50,
    ) -> Result[list[Bed], str]:
        """Get beds by status."""

    @abstractmethod
    async def count_by_status(
        self,
        tenant_id: TenantId,
    ) -> Result[dict[BedStatus, int], str]:
        """Count beds by status (for occupancy dashboard)."""
