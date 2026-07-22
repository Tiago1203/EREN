"""Shift entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import AggregateRoot, ShiftId, StaffId, TenantId, UnitId

if TYPE_CHECKING:
    pass


class ShiftStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ShiftType(str, Enum):
    DAY = "day"
    EVENING = "evening"
    NIGHT = "night"
    ON_CALL = "on_call"


@dataclass(eq=False)
class Shift(AggregateRoot):
    """Shift entity.

    Represents a work shift assigned to a staff member.

    Invariants:
    1. Shift must have exactly one assigned staff member
    2. A staff member cannot have overlapping shifts
    3. end_time must be after start_time
    """

    tenant_id: TenantId
    shift_id: ShiftId
    staff_id: StaffId

    # Timing
    shift_type: ShiftType
    start_time: datetime
    end_time: datetime

    # Assignment
    unit_id: UnitId | None = None  # capacity unit for assignment
    department_id: str | None = None

    # Status
    status: ShiftStatus = ShiftStatus.SCHEDULED
    notes: str | None = None

    # Audit

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        staff_id: StaffId,
        shift_type: ShiftType,
        start_time: datetime,
        end_time: datetime,
        unit_id: UnitId | None = None,
        department_id: str | None = None,
        notes: str | None = None,
    ) -> Shift:
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        shift_id = ShiftId.generate()
        shift = cls(
            id=shift_id,
            tenant_id=tenant_id,
            shift_id=shift_id,
            staff_id=staff_id,
            shift_type=shift_type,
            start_time=start_time,
            end_time=end_time,
            unit_id=unit_id,
            department_id=department_id,
            notes=notes,
        )
        shift._mark_created()
        return shift

    def start(self) -> None:
        if self.status != ShiftStatus.SCHEDULED:
            raise ValueError(f"Cannot start shift in {self.status.value} status")
        self._unlock_for_mutation()
        self.status = ShiftStatus.IN_PROGRESS
        self._relock_after_mutation()

    def complete(self) -> None:
        if self.status != ShiftStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete shift in {self.status.value} status")
        self._unlock_for_mutation()
        self.status = ShiftStatus.COMPLETED
        self._relock_after_mutation()

    def cancel(self) -> None:
        if self.status == ShiftStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed shift")
        self._unlock_for_mutation()
        self.status = ShiftStatus.CANCELLED
        self._relock_after_mutation()
