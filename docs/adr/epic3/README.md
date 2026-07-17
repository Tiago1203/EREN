# EREN EPIC 3 — Hospital Management ADR Index

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Architecture Board | Initial |

---

## ADR Count

| EPIC | Accepted | Proposed | Deprecated | Total |
|------|----------|----------|------------|--------|
| Epic 3 | 0 | 12 | 0 | 12 |

---

## ADR List

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0300 | Hospital Context Architecture | Proposed |
| ADR-0301 | Capacity Bounded Context | Proposed |
| ADR-0302 | Staffing Bounded Context | Proposed |
| ADR-0303 | Organization Bounded Context | Proposed |
| ADR-0304 | Department Bounded Context | Proposed |
| ADR-0305 | Asset Management Bounded Context | Proposed |
| ADR-0306 | Maintenance Bounded Context | Proposed |
| ADR-0307 | Inventory Bounded Context | Proposed |
| ADR-0308 | Organization Hierarchy Model | Proposed |
| ADR-0309 | Department Hierarchy Model | Proposed |
| ADR-0310 | Work Order Integration with Hospital | Proposed |
| ADR-0311 | Multi-Tenant Data Isolation | Proposed |

---

## Scope

Epic 3 implements the Hospital domain from EREN_THREE_DOMAINS.md:

**In scope:**
- Physical hierarchy: Hospital → Campus → Building → Floor → Room → Bed
- Organizational hierarchy: Organization → Department → Unit
- Staffing: Staff, Role, Team, Shift, Schedule
- Biomedical Engineering: Asset, Manufacturer, Vendor, Contract, Warranty
- Maintenance: Maintenance plans, preventive/corrective schedules
- Inventory: Spare parts, warehouse, purchase orders, suppliers

**Out of scope:**
- Patient, Diagnosis, Treatment (EPIC 5)
- AI reasoning (EPIC 4)
- Integrations (EPIC 6)
- UX (EPIC 7)

---

## Quick Reference

See parent: [`../../README.md`](../../README.md)

See EPIC 0: [`../../epic0/EREN_BOUNDED_CONTEXT_MAP.md`](../../epic0/EREN_BOUNDED_CONTEXT_MAP.md)

---

*EREN Epic 3 ADR Index v1.0*
*Architecture Board - 2026-07-16*
