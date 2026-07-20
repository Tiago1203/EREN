"""Entity ID primitive types for EREN.

Provides strongly-typed identifiers for all domain entities.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def _generate_uuid7() -> uuid.UUID:
    """Generate a UUID v7 (time-ordered) for better database performance.

    UUID v7 combines timestamp with random bits to create a time-ordered
    identifier that sorts correctly in databases.
    """
    # Get current timestamp in milliseconds
    timestamp_ms = int(time.time() * 1000)

    # Convert to bytes (48 bits for timestamp)
    time_bytes = timestamp_ms.to_bytes(6, "big")

    # Generate 10 random bytes
    random_bytes = uuid.uuid4().bytes[:10]

    # Combine: timestamp (6 bytes) + random (10 bytes) = 16 bytes
    combined = time_bytes + random_bytes

    # Set version (7) and variant (8) bits
    combined = bytearray(combined)
    combined[0] = (combined[0] & 0x0F) | 0x70  # Version 7
    combined[8] = (combined[8] & 0x3F) | 0x80  # Variant RFC 4122

    return uuid.UUID(bytes=bytes(combined))


@dataclass(frozen=True, slots=True)
class EntityId:
    """Strongly-typed entity identifier.

    Uses UUID v7 for time-ordered IDs with better database performance.

    Examples:
        >>> incident_id = EntityId("incident_01HX...")
        >>> device_id = EntityId("device_01HX...")
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            msg = "EntityId cannot be empty"
            raise ValueError(msg)

    @classmethod
    def generate(cls) -> EntityId:
        """Generate a new time-ordered entity ID."""
        return cls(value=f"id_{_generate_uuid7()}")

    @classmethod
    def from_uuid(cls, uuid_value: uuid.UUID) -> EntityId:
        """Create EntityId from UUID."""
        return cls(value=f"id_{uuid_value}")

    def to_uuid(self) -> uuid.UUID:
        """Convert EntityId back to UUID."""
        return uuid.UUID(self.value.replace("id_", ""))

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"EntityId({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntityId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


# Specific ID types for type safety
IncidentId = EntityId
DeviceId = EntityId
MaintenanceId = EntityId
KnowledgeId = EntityId
EngineerId = EntityId
TenantId = EntityId
OrganizationId = EntityId
LocationId = EntityId
RecommendationId = EntityId
WorkOrderId = EntityId

# EPIC 3 — Hospital Management Entity IDs
CampusId = EntityId
BuildingId = EntityId
FloorId = EntityId
RoomId = EntityId
BedId = EntityId
HospitalId = EntityId
StaffId = EntityId
RoleId = EntityId
TeamId = EntityId
ShiftId = EntityId
DepartmentId = EntityId
DepartmentGroupId = EntityId
UnitId = EntityId
DepartmentAssignmentId = EntityId
AssetId = EntityId
ManufacturerId = EntityId
VendorId = EntityId
ContractId = EntityId
WarrantyId = EntityId
SparePartId = EntityId
WarehouseId = EntityId
PurchaseOrderId = EntityId
PurchaseOrderLineItemId = EntityId
SupplierId = EntityId
MaintenancePlanId = EntityId
MaintenanceScheduleId = EntityId
MaintenanceRecordId = EntityId

