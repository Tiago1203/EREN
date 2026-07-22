"""Bed aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from core.PHASE_1.infrastructure.shared import AggregateRoot, BedId, DeviceId, RoomId, StaffId, TenantId


class BedStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    BLOCKED = "blocked"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"


class BedType(str, Enum):
    STANDARD = "standard"
    ICU = "icu"
    PEDIATRIC = "pediatric"
    NEONATAL = "neonatal"
    MATERNITY = "maternity"
    ISOLATION = "isolation"
    EMERGENCY = "emergency"


@dataclass(eq=False)
class Bed(AggregateRoot):
    """Bed aggregate root.

    The bed is the primary aggregate for the Capacity Context.
    It tracks bed availability and occupancy.

    Invariants:
    1. Bed must belong to exactly one Room
    2. Bed status transitions: available ↔ occupied ↔ blocked ↔ maintenance ↔ closed
    3. Isolation beds require negative_pressure flag = True
    4. Once closed, bed cannot be reopened
    """

    # Identity (composite key: tenant + campus + building + floor + room + bed)
    tenant_id: TenantId
    campus_id: BedId
    building_id: BedId
    floor_id: BedId
    room_id: RoomId
    bed_id: BedId

    # Attributes
    bed_number: str
    bed_type: BedType = BedType.STANDARD
    status: BedStatus = BedStatus.AVAILABLE
    negative_pressure: bool = False

    # Optional assignment
    patient_id: str | None = None  # Links to Patient Context
    device_id: DeviceId | None = None  # Monitor attached to bed
    assigned_staff_id: StaffId | None = None  # Assigned nurse/physician

    # Audit — default fields last
    occupied_at: datetime | None = None
    vacated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        campus_id: BedId,
        building_id: BedId,
        floor_id: BedId,
        room_id: RoomId,
        bed_number: str,
        bed_type: BedType = BedType.STANDARD,
        negative_pressure: bool = False,
    ) -> Bed:
        if bed_type == BedType.ISOLATION and not negative_pressure:
            raise ValueError("Isolation beds must have negative_pressure=True")
        bed_id = BedId.generate()
        bed = cls(
            id=bed_id,
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            bed_id=bed_id,
            bed_number=bed_number,
            bed_type=bed_type,
            negative_pressure=negative_pressure,
        )
        bed._mark_created()
        return bed

    # Status transitions
    def occupy(self, patient_id: str) -> None:
        """Occupies the bed with a patient."""
        if self.status not in (BedStatus.AVAILABLE, BedStatus.BLOCKED):
            raise ValueError(f"Cannot occupy bed in {self.status.value} status")
        self._unlock_for_mutation()
        self.status = BedStatus.OCCUPIED
        self.patient_id = patient_id
        self.occupied_at = datetime.now(UTC)
        self._relock_after_mutation()

    def vacate(self) -> None:
        """Vacates the bed."""
        if self.status != BedStatus.OCCUPIED:
            raise ValueError(f"Cannot vacate bed in {self.status.value} status")
        self._unlock_for_mutation()
        self.status = BedStatus.AVAILABLE
        self.patient_id = None
        self.vacated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def block(self, reason: str = "") -> None:
        """Blocks the bed temporarily."""
        if self.status == BedStatus.CLOSED:
            raise ValueError("Cannot block a closed bed")
        if self.status == BedStatus.OCCUPIED:
            raise ValueError("Cannot block an occupied bed")
        self._unlock_for_mutation()
        self.status = BedStatus.BLOCKED
        self._relock_after_mutation()

    def unblock(self) -> None:
        """Unblocks the bed."""
        if self.status != BedStatus.BLOCKED:
            raise ValueError(f"Cannot unblock bed in {self.status.value} status")
        self._unlock_for_mutation()
        self.status = BedStatus.AVAILABLE
        self._relock_after_mutation()

    def start_maintenance(self) -> None:
        """Puts bed under maintenance."""
        if self.status == BedStatus.CLOSED:
            raise ValueError("Cannot maintain a closed bed")
        self._unlock_for_mutation()
        self.status = BedStatus.MAINTENANCE
        self._relock_after_mutation()

    def close(self) -> None:
        """Permanently closes the bed."""
        if self.status == BedStatus.OCCUPIED:
            raise ValueError("Cannot close an occupied bed")
        self._unlock_for_mutation()
        self.status = BedStatus.CLOSED
        self._relock_after_mutation()

    def is_available(self) -> bool:
        """Check if bed is available for patient admission."""
        return self.status == BedStatus.AVAILABLE
