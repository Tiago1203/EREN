# EREN EPIC 3 — Hospital Management ADR Index

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Architecture Board | Initial |
| 1.1 | 2026-07-20 | Architecture Board | All ADRs Accepted — sync with master index |

---

## ADR Count

| EPIC | Accepted | Proposed | Deprecated | Total |
|------|----------|----------|------------|--------|
| Epic 3 | 12 | 0 | 0 | 12 | ✅ All Accepted |

---

## ADR List

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0300 | Hospital Context Architecture | **Accepted ✅** |
| ADR-0301 | Capacity Bounded Context | **Accepted ✅** |
| ADR-0302 | Staffing Bounded Context | **Accepted ✅** |
| ADR-0303 | Organization Bounded Context | **Accepted ✅** |
| ADR-0304 | Department Bounded Context | **Accepted ✅** |
| ADR-0305 | Asset Management Bounded Context | **Accepted ✅** |
| ADR-0306 | Maintenance Bounded Context | **Accepted ✅** |
| ADR-0307 | Inventory Bounded Context | **Accepted ✅** |
| ADR-0308 | Organization Hierarchy Model | **Accepted ✅** |
| ADR-0309 | Department Hierarchy Model | **Accepted ✅** |
| ADR-0310 | Work Order Integration with Hospital | **Accepted ✅** |
| ADR-0311 | Multi-Tenant Data Isolation | **Accepted ✅** |

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

*EREN Epic 3 ADR Index v1.1*
*Architecture Board - 2026-07-20*
