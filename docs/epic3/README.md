# EREN Epic 3 — Hospital Management Platform
*Version 1.1 - 2026-07-16*

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Architecture Board | Initial |
| 1.1 | 2026-07-16 | Architecture Board | ADRs accepted (Proposed → Accepted) |

---

## Overview

Epic 3 implements the **Hospital Management Platform** — the layer that models the physical and organizational structure of hospital organizations.

Epic 3 builds on **Epic 0** (architecture) and **Epic 1** (infrastructure) and **Epic 2** (core domain). It is a prerequisite for **Epic 5 (Clinical Intelligence)** and runs in parallel with **Epic 4 (AI Core)**.

---

## EPIC Dependencies

```
Epic 0 ──────────────────────────▶ Epic 3
Epic 1 ──────────────────────────▶ Epic 3
Epic 2 ──────────────────────────▶ Epic 3
Epic 3 ──────────────────────────▶ Epic 5
Epic 3 ──────────────────────────▶ Epic 6
Epic 4 ──────────────────────────▶ Epic 5
Epic 5 ──────────────────────────▶ Epic 7
Epic 7 ──────────────────────────▶ Epic 8
Epic 8 ──────────────────────────▶ Epic 9
Epic 9 ──────────────────────────▶ Epic 10
```

Epic 3 delivers 6 bounded contexts:

| Context | Owner | Description |
|---------|-------|-------------|
| **Capacity** | Hospital Ops | Bed, Room, Floor, Building, Campus management |
| **Staffing** | Hospital Ops | Staff, Role, Team, Shift management |
| **Organization** | Hospital Ops | Hospital, Organization, multi-campus |
| **Department** | Hospital Ops | Department, Unit, cross-cutting hierarchy |
| **Asset Management** | Biomedical | Asset, Manufacturer, Vendor, Contract, Warranty |
| **Inventory** | Hospital Ops | SpareParts, Warehouse, PurchaseOrders, Suppliers |

---

## Relationship to Epic 0

Epic 3 implements the Hospital domain decisions documented in Epic 0. Read these **in parallel** with Epic 3:

| Epic 0 Document | What Epic 3 Implements |
|-----------------|------------------------|
| `EREN_THREE_DOMAINS.md` | Hospital domain entities and relationships |
| `EREN_BOUNDED_CONTEXT_MAP.md` | Capacity, Staffing, Organization contexts |
| `EREN_DOMAIN_OWNERSHIP.md` | Bed, Room, Staff, Shift ownership |
| `EREN_DOMAIN_EVENTS_CATALOG.md` | Hospital domain events |
| `EREN_ERROR_CATALOG.md` | Hospital error codes (HOSP-*, CAP-*, LOC-*) |
| `EREN_DATA_CLASSIFICATION.md` | Hospital data classification |
| `EREN_MULTITENANCY_STRATEGY.md` | Multi-tenant data isolation |
| `EREN_CAPABILITY_MAP.md` | CapacityManagement, StaffingOptimization, InventoryManagement |

---

## Scope

### IN SCOPE — What Epic 3 IS

**Hospital Domain (physical hierarchy):**
- Hospital / Organization
- Campus
- Building
- Floor
- Room
- Bed (aggregate root — from Capacity Context)

**Organization Domain:**
- Department hierarchy (Department → Unit)
- Cross-cutting department assignments

**Staffing Domain:**
- Staff (aggregate root)
- Role
- Team
- Shift
- Schedule

**Biomedical Engineering:**
- Asset management (linked to Device Context from EPIC 2)
- Manufacturer
- Vendor
- Contract
- Warranty

**Maintenance Domain:**
- Maintenance plans
- Preventive maintenance schedules
- Corrective maintenance workflow (linked to Incident from EPIC 2)

**Inventory Domain:**
- Spare parts
- Warehouse
- Purchase orders
- Suppliers

**Infrastructure:**
- Multi-tenant data isolation (tenant_id on all Hospital tables)
- Capacity Context → Device Context integration (device location)
- Capacity Context → Clinical Context integration (bed assignment)
- Maintenance Context → Incident Context integration (linked work orders)

### NOT IN SCOPE — What Epic 3 is NOT

| Item | Belongs to | Why |
|------|------------|-----|
| Patient domain | EPIC 5 (Clinical) | Not hospital operations |
| Diagnosis domain | EPIC 5 (Clinical) | Not hospital operations |
| AI reasoning engine | EPIC 4 (AI Core) | Not domain logic |
| FHIR/HL7/MQTT integrations | EPIC 6 (Integrations) | Infrastructure |
| Web UI / Chat | EPIC 7 (UX) | Not domain logic |
| ML models | EPIC 9 (ML) | Not domain logic |

---

## Bounded Contexts

Epic 3 delivers 6 bounded contexts:

### Context: Capacity

**Owner:** Hospital Ops
**Location:** `core/capacity/`

Core entities: Bed (aggregate root), Room, Floor, Building, Campus, OccupancyRecord

### Context: Staffing

**Owner:** Hospital Ops
**Location:** `core/staffing/`

Core entities: Staff (aggregate root), Role, Team, Shift, Schedule

### Context: Organization

**Owner:** Hospital Ops
**Location:** `core/organization/`

Core entities: Hospital (aggregate root), Organization, Campus

### Context: Department

**Owner:** Hospital Ops
**Location:** `core/department/`

Core entities: Department (aggregate root), Unit, DepartmentAssignment

### Context: Asset Management

**Owner:** Biomedical
**Location:** `core/asset/`

Core entities: Asset (aggregate root), Manufacturer, Vendor, Contract, Warranty

### Context: Inventory

**Owner:** Hospital Ops
**Location:** `core/inventory/`

Core entities: SparePart (aggregate root), Warehouse, PurchaseOrder, Supplier

---

## ADR Index

| File | Title | Status |
|------|-------|--------|
| `docs/adr/epic3/ADR-0300.md` | Hospital Context Architecture | Accepted |
| `docs/adr/epic3/ADR-0301.md` | Capacity Bounded Context | Accepted |
| `docs/adr/epic3/ADR-0302.md` | Staffing Bounded Context | Accepted |
| `docs/adr/epic3/ADR-0303.md` | Organization Bounded Context | Accepted |
| `docs/adr/epic3/ADR-0304.md` | Department Bounded Context | Accepted |
| `docs/adr/epic3/ADR-0305.md` | Asset Management Bounded Context | Accepted |
| `docs/adr/epic3/ADR-0306.md` | Maintenance Bounded Context | Accepted |
| `docs/adr/epic3/ADR-0307.md` | Inventory Bounded Context | Accepted |
| `docs/adr/epic3/ADR-0308.md` | Organization Hierarchy Model | Accepted |
| `docs/adr/epic3/ADR-0309.md` | Department Hierarchy Model | Accepted |
| `docs/adr/epic3/ADR-0310.md` | Work Order Integration with Hospital | Accepted |
| `docs/adr/epic3/ADR-0311.md` | Multi-Tenant Data Isolation | Accepted |

---

## Implementation Order

```
Phase 1: Foundation
  └── Core hospital structure: Organization, Campus, Building, Floor, Room
  └── Capacity Context: Bed aggregate + occupancy tracking

Phase 2: Staffing
  └── Staff, Role, Team, Shift
  └── Staffing Context

Phase 3: Department
  └── Department hierarchy
  └── Department Context

Phase 4: Biomedical Engineering
  └── Asset, Manufacturer, Vendor, Contract, Warranty
  └── Asset Management Context

Phase 5: Maintenance
  └── Maintenance plans, preventive/corrective schedules
  └── Maintenance Context (integrates with Incident Context from EPIC 2)

Phase 6: Inventory
  └── Spare parts, warehouse, purchase orders, suppliers
  └── Inventory Context
```

---

## Hexagonal Architecture

Epic 3 follows **Hexagonal Architecture** (Ports and Adapters):

```
core/{capacity,staffing,organization,department,asset,inventory}/
├── domain/
│   ├── entities/        ← Aggregate roots
│   ├── value_objects/  ← Immutable value types
│   ├── repositories/    ← Port interfaces
│   ├── services/        ← Domain services
│   └── events/          ← Domain events
├── application/
│   ├── services/        ← Use case services
│   └── commands/        ← Command handlers
└── infrastructure/
    └── repositories/    ← SQLAlchemy adapters
```

---

## Database

PostgreSQL with multi-tenant isolation:

- All hospital tables have `tenant_id` + domain-specific ID
- RLS policies enforced (from EPIC 1 migration 007)
- Alembic migrations: `apps/api/migrations/versions/`

---

## Status: COMPLETE ✅

**Epic 3 Status:** COMPLETE ✅

All bounded contexts, SQLAlchemy models, repositories, API schemas/routers, and tests are implemented.

Completed in PR #131:
- ✅ 6 bounded contexts: Capacity, Staffing, Organization, Department, Asset Management, Inventory
- ✅ SQLAlchemy models: 21 models across 6 schema files
- ✅ Repository implementations: 6 repository classes
- ✅ API schemas: 13 schemas (bed, staff, department, asset, campus, building, floor, room, organization, hospital, team, role, warehouse, supplier, spare_part, purchase_order)
- ✅ API routers: 13 routers registered in api_router
- ✅ Alembic migration 008: All 6 schemas + 20 tables
- ✅ Unit tests: 3 new test files (organization, department, asset)
- ✅ Docs: README concatenations updated (EPIC 0→1→2→3)

**EPIC Roadmap Status:**
- EPIC 0 (Architecture) — COMPLETE ✅
- EPIC 0-Infra (Infrastructure Design) — COMPLETE ✅
- EPIC 1 (Infrastructure Platform) — COMPLETE ✅ (merged)
- EPIC 2 (Core Business Domain) — COMPLETE ✅ (merged)
- **EPIC 3 (Hospital Management) — COMPLETE ✅ (merged PR #131)**
- **EPIC 4 (AI Core) — IN PROGRESS 🚧**
- EPIC 5 (Clinical Intelligence) — Pending
- EPIC 6 (Integrations) — Pending
- EPIC 7 (User Experience) — Pending
- EPIC 8 (Production Readiness) — Pending
- EPIC 9 (Machine Learning) — Pending
- EPIC 10 (Enterprise Release) — Pending

**Next:** Epic 4 — AI Core 🚧 (see [`../epic4/README.md`](../epic4/README.md))

---

*EREN Epic 3 v1.1 - Hospital Management Platform*
*Architecture Board - 2026-07-20*
