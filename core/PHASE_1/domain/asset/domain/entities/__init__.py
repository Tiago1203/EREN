"""Asset domain entities."""

from core.PHASE_1.domain.asset.domain.entities.asset import (
    Asset,
    AssetStatus,
    DepreciationMethod,
)
from core.PHASE_1.domain.asset.domain.entities.contract import Contract, ContractStatus, ContractType
from core.PHASE_1.domain.asset.domain.entities.warranty import Warranty, WarrantyType

__all__ = [
    "Asset",
    "AssetStatus",
    "DepreciationMethod",
    "Contract",
    "ContractStatus",
    "ContractType",
    "Warranty",
    "WarrantyType",
]
