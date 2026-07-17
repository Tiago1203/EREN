"""Inventory domain entities."""

from core.inventory.domain.entities.purchase_order import PurchaseOrder, POStatus
from core.inventory.domain.entities.spare_part import PartCategory, SparePart, SparePartStatus
from core.inventory.domain.entities.supplier import Supplier, SupplierStatus, SupplierType
from core.inventory.domain.entities.warehouse import Warehouse, WarehouseStatus, WarehouseType

__all__ = [
    "PurchaseOrder",
    "POStatus",
    "PartCategory",
    "SparePart",
    "SparePartStatus",
    "Supplier",
    "SupplierStatus",
    "SupplierType",
    "Warehouse",
    "WarehouseStatus",
    "WarehouseType",
]
