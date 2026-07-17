"""SQLAlchemy models for all bounded contexts.

These models map domain entities to database tables.
They live in the infrastructure layer to preserve domain purity.
"""

from app.infrastructure.models.asset import (
    AssetModel,
    ContractModel,
    ManufacturerModel,
    VendorModel,
    WarrantyModel,
)
from app.infrastructure.models.capacity import (
    BedModel,
    BuildingModel,
    CampusModel,
    FloorModel,
    RoomModel,
)
from app.infrastructure.models.department import (
    DepartmentModel,
    UnitModel,
)
from app.infrastructure.models.device import DeviceModel
from app.infrastructure.models.incident import (
    ActionModel,
    ConversationMessageModel,
    EvidenceModel,
    IncidentModel,
    InvestigationModel,
)
from app.infrastructure.models.inventory import (
    PurchaseOrderModel,
    SparePartModel,
    SupplierModel,
    WarehouseModel,
)
from app.infrastructure.models.knowledge import DomainEventModel, KnowledgeArticleModel
from app.infrastructure.models.organization import (
    HospitalModel,
    OrganizationModel,
)
from app.infrastructure.models.recommendation import RecommendationModel
from app.infrastructure.models.staffing import (
    RoleModel,
    ShiftModel,
    StaffModel,
    TeamModel,
)
from app.infrastructure.models.work_order import WorkOrderModel

__all__ = [
    # Capacity
    "CampusModel",
    "BuildingModel",
    "FloorModel",
    "RoomModel",
    "BedModel",
    # Staffing
    "StaffModel",
    "RoleModel",
    "TeamModel",
    "ShiftModel",
    # Organization
    "OrganizationModel",
    "HospitalModel",
    # Department
    "DepartmentModel",
    "UnitModel",
    # Asset
    "AssetModel",
    "ManufacturerModel",
    "VendorModel",
    "ContractModel",
    "WarrantyModel",
    # Inventory
    "SparePartModel",
    "WarehouseModel",
    "SupplierModel",
    "PurchaseOrderModel",
    # EPIC 2
    "ActionModel",
    "ConversationMessageModel",
    "DeviceModel",
    "DomainEventModel",
    "EvidenceModel",
    "IncidentModel",
    "InvestigationModel",
    "KnowledgeArticleModel",
    "RecommendationModel",
    "WorkOrderModel",
]
