"""EREN Shared Kernel — DDD Building Blocks.

This package contains the foundational types used across all bounded contexts
in EREN. It follows the Shared Kernel pattern from DDD to ensure consistency
and avoid duplication.

Contents:
- Primitives: EntityId types
- Value Objects: Immutable value types
- Entities: BaseEntity, AggregateRoot
- Events: DomainEvent types
- Errors: Result monad, domain errors

Usage:
    from core.shared import (
        EntityId,
        IncidentId,
        ValueObject,
        AggregateRoot,
        Result,
        Ok,
        Err,
        DomainEvent,
    )

Anti-patterns to avoid:
    ❌ Don't add domain-specific types here (they belong in their context)
    ❌ Don't add business logic here (keep it in the domain layer)
    ❌ Don't add infrastructure concerns (they belong in infrastructure)
    ❌ Don't add application services (they belong in the application layer)

For adding new shared types:
    1. Does it need to be used by multiple bounded contexts?
    2. Is it a fundamental building block (not domain-specific)?
    3. Will changing it break multiple contexts?

If all answers are yes, add it here.
"""

from .entities import AggregateRoot, BaseEntity
from .errors import (
    AuthorizationError,
    ConcurrencyError,
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    Err,
    InvariantViolationError,
    InvalidStateTransitionError,
    Ok,
    Result,
    ValidationError,
)
from .events import (
    DomainEvent,
    IncidentClosed,
    IncidentEscalated,
    IncidentOpened,
    IncidentProgressed,
    IncidentReported,
    IncidentResolved,
    IncidentTriaged,
    RecommendationAccepted,
    RecommendationGenerated,
    RecommendationRejected,
)
from .primitives import (
    DeviceId,
    EngineerId,
    EntityId,
    IncidentId,
    KnowledgeId,
    LocationId,
    MaintenanceId,
    OrganizationId,
    RecommendationId,
    WorkOrderId,
    TenantId,
    # EPIC 3 — Hospital Management
    CampusId,
    BuildingId,
    FloorId,
    RoomId,
    BedId,
    HospitalId,
    StaffId,
    RoleId,
    TeamId,
    ShiftId,
    DepartmentId,
    DepartmentGroupId,
    UnitId,
    DepartmentAssignmentId,
    AssetId,
    ManufacturerId,
    VendorId,
    ContractId,
    WarrantyId,
    SparePartId,
    WarehouseId,
    PurchaseOrderId,
    PurchaseOrderLineItemId,
    SupplierId,
    MaintenancePlanId,
    MaintenanceScheduleId,
    MaintenanceRecordId,
)
from .value_objects import (
    AuditInfo,
    Confidence,
    Priority,
    SafetyLevel,
    TenantInfo,
    ValueObject,
)

__all__ = [
    # Primitives
    "EntityId",
    "IncidentId",
    "DeviceId",
    "MaintenanceId",
    "KnowledgeId",
    "EngineerId",
    "TenantId",
    "OrganizationId",
    "LocationId",
    "RecommendationId",
    # EPIC 3 — Hospital Management
    "CampusId",
    "BuildingId",
    "FloorId",
    "RoomId",
    "BedId",
    "HospitalId",
    "StaffId",
    "RoleId",
    "TeamId",
    "ShiftId",
    "DepartmentId",
    "DepartmentGroupId",
    "UnitId",
    "DepartmentAssignmentId",
    "AssetId",
    "ManufacturerId",
    "VendorId",
    "ContractId",
    "WarrantyId",
    "SparePartId",
    "WarehouseId",
    "PurchaseOrderId",
    "PurchaseOrderLineItemId",
    "SupplierId",
    "MaintenancePlanId",
    "MaintenanceScheduleId",
    "MaintenanceRecordId",
    # Value Objects
    "ValueObject",
    "Priority",
    "SafetyLevel",
    "Confidence",
    "AuditInfo",
    "TenantInfo",
    # Entities
    "BaseEntity",
    "AggregateRoot",
    # Errors
    "Result",
    "Ok",
    "Err",
    "DomainError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "InvalidStateTransitionError",
    "InvariantViolationError",
    "ValidationError",
    "ConcurrencyError",
    "AuthorizationError",
    # Events
    "DomainEvent",
    "IncidentReported",
    "IncidentTriaged",
    "IncidentOpened",
    "IncidentProgressed",
    "IncidentEscalated",
    "IncidentResolved",
    "IncidentClosed",
    "RecommendationGenerated",
    "RecommendationAccepted",
    "RecommendationRejected",
]
