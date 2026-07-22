"""Tests for EPIC 3 — Inventory Context."""

from datetime import date
from decimal import Decimal

import pytest

from core.PHASE_1.domain.inventory.domain.entities.purchase_order import POStatus, PurchaseOrder
from core.PHASE_1.domain.inventory.domain.entities.spare_part import PartCategory, SparePart, SparePartStatus
from core.PHASE_1.domain.inventory.domain.entities.supplier import Supplier, SupplierStatus, SupplierType
from core.PHASE_1.domain.inventory.domain.entities.warehouse import Warehouse, WarehouseStatus, WarehouseType


@pytest.fixture
def tenant_id() -> str:
    return "tenant_test_001"


class TestSparePart:
    def test_create_spare_part(self, tenant_id: str) -> None:
        part = SparePart.create(
            tenant_id=tenant_id,
            part_number="PUMP-MOTOR-001",
            part_name="Pump Motor Assembly",
            category=PartCategory.MECHANICAL,
            unit_cost=Decimal("150.00"),
            reorder_point=5,
            reorder_quantity=20,
            current_stock=10,
        )
        assert part.part_number == "PUMP-MOTOR-001"
        assert part.current_stock == 10
        assert not part.is_out_of_stock()

    def test_spare_part_consume(self, tenant_id: str) -> None:
        part = SparePart.create(
            tenant_id=tenant_id,
            part_number="SENSOR-TEMP-001",
            part_name="Temperature Sensor",
            category=PartCategory.ELECTRICAL,
            current_stock=10,
        )
        part.consume(3)
        assert part.current_stock == 7

    def test_spare_part_cannot_consume_more_than_available(self, tenant_id: str) -> None:
        part = SparePart.create(
            tenant_id=tenant_id,
            part_number="CABLE-USB-001",
            part_name="USB Cable",
            category=PartCategory.ELECTRICAL,
            current_stock=5,
        )
        with pytest.raises(ValueError, match="Cannot consume"):
            part.consume(10)

    def test_spare_part_restock(self, tenant_id: str) -> None:
        part = SparePart.create(
            tenant_id=tenant_id,
            part_number="FILTER-HEPA-001",
            part_name="HEPA Filter",
            category=PartCategory.MECHANICAL,
            current_stock=5,
        )
        part.restock(20)
        assert part.current_stock == 25

    def test_spare_part_below_reorder_point(self, tenant_id: str) -> None:
        part = SparePart.create(
            tenant_id=tenant_id,
            part_number="VALVE-001",
            part_name="Pressure Valve",
            category=PartCategory.MECHANICAL,
            reorder_point=10,
            current_stock=5,
        )
        assert part.is_below_reorder_point()


class TestPurchaseOrder:
    def test_create_purchase_order(self, tenant_id: str) -> None:
        supplier_id = "supplier_001"
        warehouse_id = "warehouse_main"

        po = PurchaseOrder.create(
            tenant_id=tenant_id,
            supplier_id=supplier_id,
            warehouse_id=warehouse_id,
            approval_required=True,
        )
        assert po.status == POStatus.DRAFT
        assert po.supplier_id == supplier_id
        assert po.warehouse_id == warehouse_id

    def test_purchase_order_lifecycle(self, tenant_id: str) -> None:
        po = PurchaseOrder.create(
            tenant_id=tenant_id,
            supplier_id="supplier_001",
            warehouse_id="warehouse_01",
        )
        po.submit()
        assert po.status == POStatus.SUBMITTED

        po.approve("approver_001")
        assert po.status == POStatus.APPROVED

        po.receive()
        assert po.status == POStatus.RECEIVED

    def test_purchase_order_cannot_receive_if_not_approved(self, tenant_id: str) -> None:
        po = PurchaseOrder.create(
            tenant_id=tenant_id,
            supplier_id="supplier_002",
            warehouse_id="warehouse_02",
        )
        with pytest.raises(ValueError, match="Cannot receive"):
            po.receive()

    def test_purchase_order_cannot_cancel_received(self, tenant_id: str) -> None:
        po = PurchaseOrder.create(
            tenant_id=tenant_id,
            supplier_id="supplier_003",
            warehouse_id="warehouse_03",
        )
        po.submit()
        po.approve("approver_001")
        po.receive()

        with pytest.raises(ValueError, match="Cannot cancel"):
            po.cancel()


class TestWarehouse:
    def test_create_warehouse(self, tenant_id: str) -> None:
        wh = Warehouse.create(
            tenant_id=tenant_id,
            warehouse_code="WH-MAIN",
            warehouse_name="Main Parts Warehouse",
            warehouse_type=WarehouseType.MAIN,
            address="500 Industrial Blvd",
        )
        assert wh.warehouse_code == "WH-MAIN"
        assert wh.status == WarehouseStatus.ACTIVE


class TestSupplier:
    def test_create_supplier(self, tenant_id: str) -> None:
        supplier = Supplier.create(
            tenant_id=tenant_id,
            supplier_name="MediSupply Co",
            supplier_code="MEDSUP-001",
            supplier_type=SupplierType.DISTRIBUTOR,
            lead_time_days=5,
        )
        assert supplier.supplier_name == "MediSupply Co"
        assert supplier.status == SupplierStatus.ACTIVE
