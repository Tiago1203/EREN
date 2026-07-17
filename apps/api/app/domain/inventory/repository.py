"""Inventory repository — SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.inventory import (
        SparePartModel,
        WarehouseModel,
        SupplierModel,
        PurchaseOrderModel,
    )


class InventoryRepository(Protocol):
    """Protocol for inventory bounded context."""

    async def save_spare_part(self, tenant_id: str, spare_part_id: str, **kwargs) -> "SparePartModel": ...
    async def get_spare_part(self, spare_part_id: str, tenant_id: str) -> "SparePartModel | None": ...
    async def list_spare_parts(self, tenant_id: str, warehouse_id: str | None = None, status: str | None = None, limit: int = 100) -> list["SparePartModel"]: ...
    async def update_spare_part(self, spare_part_id: str, tenant_id: str, expected_version: int, **updates) -> "SparePartModel | None": ...
    async def save_warehouse(self, tenant_id: str, warehouse_id: str, **kwargs) -> "WarehouseModel": ...
    async def get_warehouse(self, warehouse_id: str, tenant_id: str) -> "WarehouseModel | None": ...
    async def list_warehouses(self, tenant_id: str, limit: int = 100) -> list["WarehouseModel"]: ...
    async def save_supplier(self, tenant_id: str, supplier_id: str, **kwargs) -> "SupplierModel": ...
    async def get_supplier(self, supplier_id: str, tenant_id: str) -> "SupplierModel | None": ...
    async def save_purchase_order(self, tenant_id: str, purchase_order_id: str, **kwargs) -> "PurchaseOrderModel": ...
    async def get_purchase_order(self, purchase_order_id: str, tenant_id: str) -> "PurchaseOrderModel | None": ...
    async def list_purchase_orders(self, tenant_id: str, supplier_id: str | None = None, status: str | None = None, limit: int = 100) -> list["PurchaseOrderModel"]: ...
    async def update_purchase_order(self, purchase_order_id: str, tenant_id: str, expected_version: int, **updates) -> "PurchaseOrderModel | None": ...


@dataclass
class SQLAlchemyInventoryRepository:
    """SQLAlchemy implementation of InventoryRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _save(self, model):
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return model

    async def save_spare_part(self, tenant_id: str, spare_part_id: str, **kwargs) -> "SparePartModel":
        from app.infrastructure.models.inventory import SparePartModel
        model = SparePartModel(
            id=UUID(spare_part_id), tenant_id=tenant_id, spare_part_id=spare_part_id, **kwargs
        )
        return await self._save(model)

    async def get_spare_part(self, spare_part_id: str, tenant_id: str) -> "SparePartModel | None":
        from app.infrastructure.models.inventory import SparePartModel
        stmt = select(SparePartModel).where(
            SparePartModel.spare_part_id == spare_part_id,
            SparePartModel.tenant_id == tenant_id,
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_spare_parts(
        self, tenant_id: str, warehouse_id: str | None = None, status: str | None = None, limit: int = 100
    ) -> list["SparePartModel"]:
        from app.infrastructure.models.inventory import SparePartModel
        stmt = select(SparePartModel).where(SparePartModel.tenant_id == tenant_id)
        if warehouse_id:
            stmt = stmt.where(SparePartModel.warehouse_id == warehouse_id)
        if status:
            stmt = stmt.where(SparePartModel.status == status)
        stmt = stmt.limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def update_spare_part(
        self, spare_part_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "SparePartModel | None":
        from app.infrastructure.models.inventory import SparePartModel
        stmt = select(SparePartModel).where(
            SparePartModel.spare_part_id == spare_part_id,
            SparePartModel.tenant_id == tenant_id,
        )
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None or model.version != expected_version:
            return None
        for key, value in updates.items():
            if hasattr(model, key):
                setattr(model, key, value)
        model.version = expected_version + 1
        model.updated_at = datetime.now()
        await self._db.commit()
        await self._db.refresh(model)
        return model

    async def save_warehouse(self, tenant_id: str, warehouse_id: str, **kwargs) -> "WarehouseModel":
        from app.infrastructure.models.inventory import WarehouseModel
        model = WarehouseModel(
            id=UUID(warehouse_id), tenant_id=tenant_id, warehouse_id=warehouse_id, **kwargs
        )
        return await self._save(model)

    async def get_warehouse(self, warehouse_id: str, tenant_id: str) -> "WarehouseModel | None":
        from app.infrastructure.models.inventory import WarehouseModel
        stmt = select(WarehouseModel).where(
            WarehouseModel.warehouse_id == warehouse_id,
            WarehouseModel.tenant_id == tenant_id,
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_warehouses(self, tenant_id: str, limit: int = 100) -> list["WarehouseModel"]:
        from app.infrastructure.models.inventory import WarehouseModel
        stmt = select(WarehouseModel).where(WarehouseModel.tenant_id == tenant_id).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def save_supplier(self, tenant_id: str, supplier_id: str, **kwargs) -> "SupplierModel":
        from app.infrastructure.models.inventory import SupplierModel
        model = SupplierModel(
            id=UUID(supplier_id), tenant_id=tenant_id, supplier_id=supplier_id, **kwargs
        )
        return await self._save(model)

    async def get_supplier(self, supplier_id: str, tenant_id: str) -> "SupplierModel | None":
        from app.infrastructure.models.inventory import SupplierModel
        stmt = select(SupplierModel).where(
            SupplierModel.supplier_id == supplier_id,
            SupplierModel.tenant_id == tenant_id,
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_purchase_order(self, tenant_id: str, purchase_order_id: str, **kwargs) -> "PurchaseOrderModel":
        from app.infrastructure.models.inventory import PurchaseOrderModel
        model = PurchaseOrderModel(
            id=UUID(purchase_order_id), tenant_id=tenant_id, purchase_order_id=purchase_order_id, **kwargs
        )
        return await self._save(model)

    async def get_purchase_order(self, purchase_order_id: str, tenant_id: str) -> "PurchaseOrderModel | None":
        from app.infrastructure.models.inventory import PurchaseOrderModel
        stmt = select(PurchaseOrderModel).where(
            PurchaseOrderModel.purchase_order_id == purchase_order_id,
            PurchaseOrderModel.tenant_id == tenant_id,
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_purchase_orders(
        self, tenant_id: str, supplier_id: str | None = None, status: str | None = None, limit: int = 100
    ) -> list["PurchaseOrderModel"]:
        from app.infrastructure.models.inventory import PurchaseOrderModel
        stmt = select(PurchaseOrderModel).where(PurchaseOrderModel.tenant_id == tenant_id)
        if supplier_id:
            stmt = stmt.where(PurchaseOrderModel.supplier_id == supplier_id)
        if status:
            stmt = stmt.where(PurchaseOrderModel.status == status)
        stmt = stmt.limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def update_purchase_order(
        self, purchase_order_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "PurchaseOrderModel | None":
        from app.infrastructure.models.inventory import PurchaseOrderModel
        stmt = select(PurchaseOrderModel).where(
            PurchaseOrderModel.purchase_order_id == purchase_order_id,
            PurchaseOrderModel.tenant_id == tenant_id,
        )
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None or model.version != expected_version:
            return None
        for key, value in updates.items():
            if hasattr(model, key):
                setattr(model, key, value)
        model.version = expected_version + 1
        model.updated_at = datetime.now()
        await self._db.commit()
        await self._db.refresh(model)
        return model
