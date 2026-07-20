"""Repository interface for Staff aggregate."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from core.shared import Result, ShiftId, StaffId, TenantId

from ..entities.staff import Staff, StaffType


class StaffRepository(ABC):
    """Repository interface for Staff aggregate."""

    @abstractmethod
    async def save(self, staff: Staff) -> Result[Staff, str]:
        """Save a staff member."""

    @abstractmethod
    async def get_by_id(self, staff_id: StaffId) -> Result[Staff | None, str]:
        """Get a staff member by ID."""

    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[Staff], str]:
        """Get all staff for a tenant."""

    @abstractmethod
    async def get_by_type(
        self,
        tenant_id: TenantId,
        staff_type: StaffType,
    ) -> Result[list[Staff], str]:
        """Get staff by type (physician, nurse, etc.)."""

    @abstractmethod
    async def get_active(
        self,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[Staff], str]:
        """Get all active (non-terminated) staff."""

    @abstractmethod
    async def get_by_shift(
        self,
        shift_id: ShiftId,
    ) -> Result[Staff | None, str]:
        """Get staff assigned to a shift."""

    @abstractmethod
    async def get_by_department(
        self,
        tenant_id: TenantId,
        department_id: str,
    ) -> Result[list[Staff], str]:
        """Get staff assigned to a department."""

    @abstractmethod
    async def get_upcoming_shifts(
        self,
        tenant_id: TenantId,
        staff_id: StaffId,
        from_time: datetime,
    ) -> Result[list, str]:
        """Get upcoming shifts for a staff member."""
