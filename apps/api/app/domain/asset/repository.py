"""Asset repository — SQLAlchemy implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

if TYPE_CHECKING:
    from app.infrastructure.models.asset import (
        AssetModel,
        ManufacturerModel,
        VendorModel,
        ContractModel,
        WarrantyModel,
    )


class AssetRepository(Protocol):
    """Protocol for asset bounded context."""

    async def save_asset(self, tenant_id: str, asset_id: str, **kwargs) -> "AssetModel": ...
    async def get_asset(self, asset_id: str, tenant_id: str) -> "AssetModel | None": ...
    async def list_assets(self, tenant_id: str, status: str | None = None, device_id: str | None = None, limit: int = 100) -> list["AssetModel"]: ...
    async def update_asset(self, asset_id: str, tenant_id: str, expected_version: int, **updates) -> "AssetModel | None": ...
    async def save_contract(self, tenant_id: str, contract_id: str, **kwargs) -> "ContractModel": ...
    async def get_contract(self, contract_id: str, tenant_id: str) -> "ContractModel | None": ...
    async def list_contracts(self, tenant_id: str, asset_id: str | None = None, limit: int = 100) -> list["ContractModel"]: ...
    async def save_warranty(self, tenant_id: str, warranty_id: str, **kwargs) -> "WarrantyModel": ...
    async def get_warranty(self, warranty_id: str, tenant_id: str) -> "WarrantyModel | None": ...


@dataclass
class SQLAlchemyAssetRepository:
    """SQLAlchemy implementation of AssetRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _save(self, model):
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return model

    async def save_asset(self, tenant_id: str, asset_id: str, **kwargs) -> "AssetModel":
        from app.infrastructure.models.asset import AssetModel
        model = AssetModel(id=UUID(asset_id), tenant_id=tenant_id, asset_id=asset_id, **kwargs)
        return await self._save(model)

    async def get_asset(self, asset_id: str, tenant_id: str) -> "AssetModel | None":
        from app.infrastructure.models.asset import AssetModel
        stmt = select(AssetModel).where(
            AssetModel.asset_id == asset_id, AssetModel.tenant_id == tenant_id
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_assets(
        self, tenant_id: str, status: str | None = None, device_id: str | None = None, limit: int = 100
    ) -> list["AssetModel"]:
        from app.infrastructure.models.asset import AssetModel
        stmt = select(AssetModel).where(AssetModel.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(AssetModel.status == status)
        if device_id:
            stmt = stmt.where(AssetModel.device_id == device_id)
        stmt = stmt.limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def update_asset(
        self, asset_id: str, tenant_id: str, expected_version: int, **updates
    ) -> "AssetModel | None":
        from app.infrastructure.models.asset import AssetModel
        stmt = select(AssetModel).where(
            AssetModel.asset_id == asset_id, AssetModel.tenant_id == tenant_id
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

    async def save_contract(self, tenant_id: str, contract_id: str, **kwargs) -> "ContractModel":
        from app.infrastructure.models.asset import ContractModel
        model = ContractModel(id=UUID(contract_id), tenant_id=tenant_id, contract_id=contract_id, **kwargs)
        return await self._save(model)

    async def get_contract(self, contract_id: str, tenant_id: str) -> "ContractModel | None":
        from app.infrastructure.models.asset import ContractModel
        stmt = select(ContractModel).where(
            ContractModel.contract_id == contract_id, ContractModel.tenant_id == tenant_id
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_contracts(
        self, tenant_id: str, asset_id: str | None = None, limit: int = 100
    ) -> list["ContractModel"]:
        from app.infrastructure.models.asset import ContractModel
        stmt = select(ContractModel).where(ContractModel.tenant_id == tenant_id)
        if asset_id:
            stmt = stmt.where(ContractModel.asset_id == asset_id)
        stmt = stmt.limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def save_warranty(self, tenant_id: str, warranty_id: str, **kwargs) -> "WarrantyModel":
        from app.infrastructure.models.asset import WarrantyModel
        model = WarrantyModel(id=UUID(warranty_id), tenant_id=tenant_id, warranty_id=warranty_id, **kwargs)
        return await self._save(model)

    async def get_warranty(self, warranty_id: str, tenant_id: str) -> "WarrantyModel | None":
        from app.infrastructure.models.asset import WarrantyModel
        stmt = select(WarrantyModel).where(
            WarrantyModel.warranty_id == warranty_id, WarrantyModel.tenant_id == tenant_id
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()
