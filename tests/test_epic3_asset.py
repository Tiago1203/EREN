"""Unit tests for Asset Management bounded context (EPIC 3)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from core.asset.domain.entities import Asset, Contract, Warranty
from core.asset.domain.entities import AssetStatus, ContractType, ContractStatus, WarrantyType
from core.asset.domain.entities import DepreciationMethod
from core.shared import AssetId, ContractId, WarrantyId, TenantId, DeviceId, VendorId


class TestAsset:
    def test_create_asset(self):
        asset = Asset.create(
            tenant_id=TenantId.generate(),
            asset_tag="AST-001",
            name="Portable X-Ray Machine",
        )
        assert asset.asset_tag == "AST-001"
        assert asset.name == "Portable X-Ray Machine"
        assert asset.status == AssetStatus.ACTIVE

    def test_asset_depreciation(self):
        """Asset can be configured with depreciation settings."""
        asset = Asset.create(
            tenant_id=TenantId.generate(),
            asset_tag="AST-002",
            name="MRI Scanner",
            acquisition_cost=Decimal("100000.00"),
            useful_life_years=10,
            depreciation_method=DepreciationMethod.STRAIGHT_LINE,
            acquisition_date=date.today(),
        )
        assert asset.acquisition_cost == Decimal("100000.00")
        assert asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE
        assert asset.current_value == Decimal("100000.00")  # initial = acquisition

    def test_asset_device_linkage(self):
        """Asset tracks device linkage."""
        asset = Asset.create(
            tenant_id=TenantId.generate(),
            asset_tag="AST-003",
            name="Infusion Pump",
        )
        assert asset.device_id is None  # Not linked initially


class TestContract:
    def test_create_service_contract(self):
        asset = Asset.create(
            tenant_id=TenantId.generate(),
            asset_tag="AST-005",
            name="CT Scanner",
        )
        vendor_id = VendorId.generate()
        contract = Contract.create(
            tenant_id=asset.tenant_id,
            asset_id=asset.id,
            vendor_id=vendor_id,
            contract_number="SVC-001",
            contract_type=ContractType.SERVICE,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            total_value=Decimal("50000.00"),
        )
        assert contract.contract_type == ContractType.SERVICE
        assert contract.status == ContractStatus.ACTIVE

    def test_contract_auto_renew(self):
        asset = Asset.create(
            tenant_id=TenantId.generate(),
            asset_tag="AST-006",
            name="X-Ray",
        )
        vendor_id = VendorId.generate()
        contract = Contract.create(
            tenant_id=asset.tenant_id,
            asset_id=asset.id,
            vendor_id=vendor_id,
            contract_number="SVC-002",
            contract_type=ContractType.SERVICE,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            total_value=Decimal("10000.00"),
            auto_renew=True,
        )
        assert contract.auto_renew is True

    def test_contract_is_active(self):
        asset = Asset.create(
            tenant_id=TenantId.generate(),
            asset_tag="AST-007",
            name="Ultrasound",
        )
        vendor_id = VendorId.generate()
        contract = Contract.create(
            tenant_id=asset.tenant_id,
            asset_id=asset.id,
            vendor_id=vendor_id,
            contract_number="SVC-003",
            contract_type=ContractType.SERVICE,
            start_date=date.today() - timedelta(days=100),
            end_date=date.today() + timedelta(days=265),
            total_value=Decimal("5000.00"),
        )
        assert contract.is_active() is True


class TestWarranty:
    def test_create_warranty(self):
        asset = Asset.create(
            tenant_id=TenantId.generate(),
            asset_tag="AST-008",
            name="Defibrillator",
        )
        warranty = Warranty.create(
            tenant_id=asset.tenant_id,
            asset_id=asset.id,
            warranty_type=WarrantyType.MANUFACTURER,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=730),
            warranty_provider="Manufacturer Inc",
        )
        assert warranty.is_active() is True
        assert warranty.warranty_type == WarrantyType.MANUFACTURER

    def test_warranty_active_check(self):
        asset = Asset.create(
            tenant_id=TenantId.generate(),
            asset_tag="AST-009",
            name="ECG Machine",
        )
        # Active warranty
        active = Warranty.create(
            tenant_id=asset.tenant_id,
            asset_id=asset.id,
            warranty_type=WarrantyType.MANUFACTURER,
            start_date=date.today() - timedelta(days=100),
            end_date=date.today() + timedelta(days=265),
        )
        assert active.is_active() is True
        # Expired warranty
        expired = Warranty.create(
            tenant_id=asset.tenant_id,
            asset_id=asset.id,
            warranty_type=WarrantyType.EXTENDED,
            start_date=date.today() - timedelta(days=400),
            end_date=date.today() - timedelta(days=35),
        )
        assert expired.is_active() is False
