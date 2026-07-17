"""Create hospital capacity schema.

Revision ID: 008
Revises: 007_rls_enforcement
Create Date: 2026-07-16

Tables:
- capacity.campuses
- capacity.buildings
- capacity.floors
- capacity.rooms
- capacity.beds

EPIC 3 — Hospital Management Platform
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "008"
down_revision = "007_rls_enforcement"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Capacity Schema ────────────────────────────────────────────────────────
    op.execute('CREATE SCHEMA IF NOT EXISTS "capacity"')

    # ── Campuses ──────────────────────────────────────────────────────────────
    op.create_table(
        "campuses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("campus_id", sa.String(36), nullable=False, unique=True),
        sa.Column("campus_code", sa.String(20), nullable=False),
        sa.Column("campus_name", sa.String(200), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="capacity",
    )
    op.create_index("ix_campuses_tenant_id", "campuses", ["tenant_id"], schema="capacity")
    op.create_index("ix_campuses_organization_id", "campuses", ["organization_id"], schema="capacity")
    op.create_index("ix_campuses_campus_code", "campuses", ["campus_code"], schema="capacity")

    # ── Buildings ──────────────────────────────────────────────────────────────
    op.create_table(
        "buildings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("campus_id", sa.String(36), nullable=False),
        sa.Column("building_id", sa.String(36), nullable=False, unique=True),
        sa.Column("building_code", sa.String(20), nullable=False),
        sa.Column("building_name", sa.String(200), nullable=False),
        sa.Column("building_type", sa.String(20), nullable=False, server_default="main"),
        sa.Column("status", sa.String(20), nullable=False, server_default="operational"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="capacity",
    )
    op.create_index("ix_buildings_tenant_id", "buildings", ["tenant_id"], schema="capacity")
    op.create_index("ix_buildings_campus_id", "buildings", ["campus_id"], schema="capacity")
    op.create_index("ix_buildings_building_code", "buildings", ["building_code"], schema="capacity")

    # ── Floors ────────────────────────────────────────────────────────────────
    op.create_table(
        "floors",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("building_id", sa.String(36), nullable=False),
        sa.Column("floor_id", sa.String(36), nullable=False, unique=True),
        sa.Column("floor_number", sa.Integer(), nullable=False),
        sa.Column("floor_type", sa.String(20), nullable=False, server_default="standard"),
        sa.Column("status", sa.String(20), nullable=False, server_default="operational"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="capacity",
    )
    op.create_index("ix_floors_tenant_id", "floors", ["tenant_id"], schema="capacity")
    op.create_index("ix_floors_building_id", "floors", ["building_id"], schema="capacity")

    # ── Rooms ─────────────────────────────────────────────────────────────────
    op.create_table(
        "rooms",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("floor_id", sa.String(36), nullable=False),
        sa.Column("room_id", sa.String(36), nullable=False, unique=True),
        sa.Column("room_number", sa.String(50), nullable=False),
        sa.Column("room_type", sa.String(20), nullable=False, server_default="patient"),
        sa.Column("bed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="operational"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="capacity",
    )
    op.create_index("ix_rooms_tenant_id", "rooms", ["tenant_id"], schema="capacity")
    op.create_index("ix_rooms_floor_id", "rooms", ["floor_id"], schema="capacity")
    op.create_index("ix_rooms_room_number", "rooms", ["room_number"], schema="capacity")

    # ── Beds ─────────────────────────────────────────────────────────────────
    op.create_table(
        "beds",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("campus_id", sa.String(36), nullable=True),
        sa.Column("building_id", sa.String(36), nullable=True),
        sa.Column("floor_id", sa.String(36), nullable=True),
        sa.Column("room_id", sa.String(36), nullable=False),
        sa.Column("bed_id", sa.String(36), nullable=False, unique=True),
        sa.Column("bed_number", sa.String(50), nullable=False),
        sa.Column("bed_type", sa.String(20), nullable=False, server_default="standard"),
        sa.Column("status", sa.String(20), nullable=False, server_default="available"),
        sa.Column("negative_pressure", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("patient_id", sa.String(100), nullable=True),
        sa.Column("device_id", sa.String(36), nullable=True),
        sa.Column("assigned_staff_id", sa.String(36), nullable=True),
        sa.Column("occupied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("vacated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="capacity",
    )
    op.create_index("ix_beds_tenant_id", "beds", ["tenant_id"], schema="capacity")
    op.create_index("ix_beds_room_id", "beds", ["room_id"], schema="capacity")
    op.create_index("ix_beds_status", "beds", ["status"], schema="capacity")
    op.create_index("ix_beds_bed_type", "beds", ["bed_type"], schema="capacity")
    op.create_index("ix_beds_patient_id", "beds", ["patient_id"], schema="capacity")

    # ── Staffing Schema ────────────────────────────────────────────────────────
    op.execute('CREATE SCHEMA IF NOT EXISTS "staffing"')

    op.create_table(
        "staff",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("staff_id", sa.String(36), nullable=False, unique=True),
        sa.Column("employee_id", sa.String(50), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("staff_type", sa.String(20), nullable=False),
        sa.Column("employment_status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column("primary_role_id", sa.String(36), nullable=True),
        sa.Column("team_ids", sa.JSON(), nullable=True, server_default="[]"),
        sa.Column("terminated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="staffing",
    )
    op.create_index("ix_staff_tenant_id", "staff", ["tenant_id"], schema="staffing")
    op.create_index("ix_staff_staff_type", "staff", ["staff_type"], schema="staffing")
    op.create_index("ix_staff_employment_status", "staff", ["employment_status"], schema="staffing")
    op.create_index("ix_staff_email", "staff", ["email"], schema="staffing")

    op.create_table(
        "shifts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("shift_id", sa.String(36), nullable=False, unique=True),
        sa.Column("staff_id", sa.String(36), nullable=False),
        sa.Column("shift_type", sa.String(20), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("unit_id", sa.String(36), nullable=True),
        sa.Column("department_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="scheduled"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="staffing",
    )
    op.create_index("ix_shifts_tenant_id", "shifts", ["tenant_id"], schema="staffing")
    op.create_index("ix_shifts_staff_id", "shifts", ["staff_id"], schema="staffing")
    op.create_index("ix_shifts_status", "shifts", ["status"], schema="staffing")

    # ── Organization Schema ────────────────────────────────────────────────────
    op.execute('CREATE SCHEMA IF NOT EXISTS "organization"')

    op.create_table(
        "organizations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False, unique=True),
        sa.Column("legal_name", sa.String(255), nullable=False),
        sa.Column("doing_business_as", sa.String(255), nullable=True),
        sa.Column("tax_id", sa.String(50), nullable=True),
        sa.Column("ownership_type", sa.String(20), nullable=False, server_default="private"),
        sa.Column("founded_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="organization",
    )
    op.create_index("ix_organizations_tenant_id", "organizations", ["tenant_id"], schema="organization")

    op.create_table(
        "hospitals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("hospital_id", sa.String(36), nullable=False, unique=True),
        sa.Column("hospital_code", sa.String(20), nullable=False),
        sa.Column("hospital_name", sa.String(200), nullable=False),
        sa.Column("hospital_type", sa.String(20), nullable=False),
        sa.Column("license_number", sa.String(100), nullable=True),
        sa.Column("accreditation_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("license_expiry_date", sa.Date(), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="organization",
    )
    op.create_index("ix_hospitals_tenant_id", "hospitals", ["tenant_id"], schema="organization")
    op.create_index("ix_hospitals_organization_id", "hospitals", ["organization_id"], schema="organization")
    op.create_index("ix_hospitals_hospital_code", "hospitals", ["hospital_code"], schema="organization")

    # ── Department Schema ─────────────────────────────────────────────────────
    op.execute('CREATE SCHEMA IF NOT EXISTS "department"')

    op.create_table(
        "departments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("department_id", sa.String(36), nullable=False, unique=True),
        sa.Column("department_code", sa.String(50), nullable=False),
        sa.Column("department_name", sa.String(200), nullable=False),
        sa.Column("department_type", sa.String(20), nullable=False),
        sa.Column("parent_department_id", sa.String(36), nullable=True),
        sa.Column("department_group_id", sa.String(36), nullable=True),
        sa.Column("cost_center", sa.String(50), nullable=True),
        sa.Column("budget_allocated", sa.Numeric(15, 2), nullable=True),
        sa.Column("head_staff_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="department",
    )
    op.create_index("ix_departments_tenant_id", "departments", ["tenant_id"], schema="department")
    op.create_index("ix_departments_organization_id", "departments", ["organization_id"], schema="department")

    op.create_table(
        "units",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("department_id", sa.String(36), nullable=False),
        sa.Column("unit_id", sa.String(36), nullable=False, unique=True),
        sa.Column("unit_code", sa.String(50), nullable=False),
        sa.Column("unit_name", sa.String(200), nullable=False),
        sa.Column("unit_type", sa.String(20), nullable=False, server_default="inpatient"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="department",
    )
    op.create_index("ix_units_tenant_id", "units", ["tenant_id"], schema="department")
    op.create_index("ix_units_department_id", "units", ["department_id"], schema="department")

    # ── Asset Schema ────────────────────────────────────────────────────────────
    op.execute('CREATE SCHEMA IF NOT EXISTS "asset"')

    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("asset_id", sa.String(36), nullable=False, unique=True),
        sa.Column("asset_tag", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("device_id", sa.String(36), nullable=True),
        sa.Column("manufacturer_id", sa.String(36), nullable=True),
        sa.Column("vendor_id", sa.String(36), nullable=True),
        sa.Column("acquisition_date", sa.Date(), nullable=True),
        sa.Column("acquisition_cost", sa.Numeric(15, 2), nullable=False, server_default="0.00"),
        sa.Column("current_value", sa.Numeric(15, 2), nullable=False, server_default="0.00"),
        sa.Column("depreciation_method", sa.String(20), nullable=False, server_default="straight_line"),
        sa.Column("useful_life_years", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("location_id", sa.String(36), nullable=True),
        sa.Column("department_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("active_contract_id", sa.String(36), nullable=True),
        sa.Column("active_warranty_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="asset",
    )
    op.create_index("ix_assets_tenant_id", "assets", ["tenant_id"], schema="asset")
    op.create_index("ix_assets_asset_tag", "assets", ["asset_tag"], schema="asset")
    op.create_index("ix_assets_device_id", "assets", ["device_id"], schema="asset")
    op.create_index("ix_assets_status", "assets", ["status"], schema="asset")

    op.create_table(
        "contracts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("contract_id", sa.String(36), nullable=False, unique=True),
        sa.Column("asset_id", sa.String(36), nullable=False),
        sa.Column("vendor_id", sa.String(36), nullable=False),
        sa.Column("contract_number", sa.String(50), nullable=False),
        sa.Column("contract_type", sa.String(20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_value", sa.Numeric(15, 2), nullable=False, server_default="0.00"),
        sa.Column("payment_terms", sa.String(100), nullable=True),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("renewal_terms", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="asset",
    )
    op.create_index("ix_contracts_tenant_id", "contracts", ["tenant_id"], schema="asset")
    op.create_index("ix_contracts_asset_id", "contracts", ["asset_id"], schema="asset")
    op.create_index("ix_contracts_vendor_id", "contracts", ["vendor_id"], schema="asset")

    # ── Inventory Schema ──────────────────────────────────────────────────────
    op.execute('CREATE SCHEMA IF NOT EXISTS "inventory"')

    op.create_table(
        "spare_parts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("spare_part_id", sa.String(36), nullable=False, unique=True),
        sa.Column("part_number", sa.String(50), nullable=False),
        sa.Column("part_name", sa.String(200), nullable=False),
        sa.Column("part_description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("manufacturer_id", sa.String(36), nullable=True),
        sa.Column("unit_of_measure", sa.String(20), nullable=False, server_default="piece"),
        sa.Column("unit_cost", sa.Numeric(15, 2), nullable=False, server_default="0.00"),
        sa.Column("reorder_point", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reorder_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warehouse_id", sa.String(36), nullable=True),
        sa.Column("storage_location", sa.String(50), nullable=True),
        sa.Column("lot_tracking_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("expiry_tracking_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("shelf_life_days", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="inventory",
    )
    op.create_index("ix_spare_parts_tenant_id", "spare_parts", ["tenant_id"], schema="inventory")
    op.create_index("ix_spare_parts_part_number", "spare_parts", ["part_number"], schema="inventory")
    op.create_index("ix_spare_parts_warehouse_id", "spare_parts", ["warehouse_id"], schema="inventory")
    op.create_index("ix_spare_parts_status", "spare_parts", ["status"], schema="inventory")

    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("purchase_order_id", sa.String(36), nullable=False, unique=True),
        sa.Column("po_number", sa.String(30), nullable=False),
        sa.Column("supplier_id", sa.String(36), nullable=False),
        sa.Column("warehouse_id", sa.String(36), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("expected_delivery_date", sa.Date(), nullable=True),
        sa.Column("total_value", sa.Numeric(15, 2), nullable=False, server_default="0.00"),
        sa.Column("approval_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("approved_by_staff_id", sa.String(36), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="inventory",
    )
    op.create_index("ix_purchase_orders_tenant_id", "purchase_orders", ["tenant_id"], schema="inventory")
    op.create_index("ix_purchase_orders_supplier_id", "purchase_orders", ["supplier_id"], schema="inventory")
    op.create_index("ix_purchase_orders_status", "purchase_orders", ["status"], schema="inventory")


def downgrade() -> None:
    op.drop_table("purchase_orders", schema="inventory")
    op.drop_table("spare_parts", schema="inventory")
    op.execute('DROP SCHEMA IF EXISTS "inventory" CASCADE')

    op.drop_table("contracts", schema="asset")
    op.drop_table("assets", schema="asset")
    op.execute('DROP SCHEMA IF EXISTS "asset" CASCADE')

    op.drop_table("units", schema="department")
    op.drop_table("departments", schema="department")
    op.execute('DROP SCHEMA IF EXISTS "department" CASCADE')

    op.drop_table("hospitals", schema="organization")
    op.drop_table("organizations", schema="organization")
    op.execute('DROP SCHEMA IF EXISTS "organization" CASCADE')

    op.drop_table("shifts", schema="staffing")
    op.drop_table("staff", schema="staffing")
    op.execute('DROP SCHEMA IF EXISTS "staffing" CASCADE')

    op.drop_table("beds", schema="capacity")
    op.drop_table("rooms", schema="capacity")
    op.drop_table("floors", schema="capacity")
    op.drop_table("buildings", schema="capacity")
    op.drop_table("campuses", schema="capacity")
    op.execute('DROP SCHEMA IF EXISTS "capacity" CASCADE')
