"""Unit tests for Department bounded context (EPIC 3)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from core.department.domain.entities import Department, Unit
from core.department.domain.entities import DepartmentType, DepartmentStatus, UnitType, UnitStatus
from core.shared import DepartmentId, UnitId, TenantId, OrganizationId


class TestDepartment:
    def test_create_department(self):
        dept = Department.create(
            tenant_id=TenantId.generate(),
            organization_id=OrganizationId.generate(),
            department_code="ICU",
            department_name="Intensive Care Unit",
            department_type=DepartmentType.CLINICAL,
        )
        assert dept.department_code == "ICU"
        assert dept.department_name == "Intensive Care Unit"
        assert dept.department_type == DepartmentType.CLINICAL
        assert dept.status == DepartmentStatus.ACTIVE

    def test_department_hierarchy(self):
        parent = Department.create(
            tenant_id=TenantId.generate(),
            organization_id=OrganizationId.generate(),
            department_code="MED",
            department_name="Medical",
            department_type=DepartmentType.CLINICAL,
        )
        child = Department.create(
            tenant_id=parent.tenant_id,
            organization_id=parent.organization_id,
            department_code="CARDIO",
            department_name="Cardiology",
            department_type=DepartmentType.CLINICAL,
            parent_department_id=parent.id,
        )
        assert child.parent_department_id == parent.id
        assert child.parent_department_id is not None
        assert parent.parent_department_id is None

    def test_department_budget(self):
        dept = Department.create(
            tenant_id=TenantId.generate(),
            organization_id=OrganizationId.generate(),
            department_code="ADMIN",
            department_name="Administration",
            department_type=DepartmentType.ADMINISTRATIVE,
            cost_center="CC-001",
            budget_allocated=Decimal("1000000.00"),
        )
        assert dept.budget_allocated == Decimal("1000000.00")
        assert dept.cost_center == "CC-001"


class TestUnit:
    def test_create_unit(self):
        dept = Department.create(
            tenant_id=TenantId.generate(),
            organization_id=OrganizationId.generate(),
            department_code="ICU",
            department_name="ICU",
            department_type=DepartmentType.CLINICAL,
        )
        unit = Unit.create(
            tenant_id=dept.tenant_id,
            organization_id=dept.organization_id,
            department_id=dept.id,
            unit_code="ICU-1",
            unit_name="ICU Bed 1",
            unit_type=UnitType.ICU,
        )
        assert unit.unit_code == "ICU-1"
        assert unit.department_id == dept.id
        assert unit.status == UnitStatus.ACTIVE

    def test_unit_creation_under_department(self):
        """Unit can be created under a specific department."""
        dept = Department.create(
            tenant_id=TenantId.generate(),
            organization_id=OrganizationId.generate(),
            department_code="TEST",
            department_name="Test",
            department_type=DepartmentType.SUPPORT,
        )
        unit = Unit.create(
            tenant_id=dept.tenant_id,
            organization_id=dept.organization_id,
            department_id=dept.id,
            unit_code="TEST-1",
            unit_name="Test Unit",
            unit_type=UnitType.INPATIENT,
        )
        assert unit.unit_code == "TEST-1"
        assert unit.department_id == dept.id
        assert unit.status == UnitStatus.ACTIVE
