# EREN ADR Index
## Architecture Decision Records

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |

---

## Purpose

This index tracks all Architecture Decision Records (ADRs) for EREN. Every significant architectural decision must have an ADR.

**Rule:** No architectural decision without an ADR. No ADR without a status.

---

## ADR Status Definitions

| Status | Meaning |
|--------|---------|
| **Proposed** | Under review, not yet accepted |
| **Accepted** | Approved and in effect |
| **Superseded** | Replaced by a newer ADR |
| **Deprecated** | No longer relevant |
| **Rejected** | Considered but not adopted |

---

## ADRs by Domain

### Core Architecture

| ADR | Title | Status | Date | Owner |
|-----|-------|--------|------|-------|
| ADR-0001 | Hexagonal Architecture | ✅ Accepted | 2026-01-15 | Architecture Board |
| ADR-0002 | PostgreSQL as Primary Database | ✅ Accepted | 2026-01-15 | Architecture Board |
| ADR-0003 | Event-Driven Architecture | ✅ Accepted | 2026-02-01 | Architecture Board |
| ADR-0004 | Redis Cache-Aside Pattern | ✅ Accepted | 2026-02-01 | Architecture Board |
| ADR-0005 | Neo4j for Knowledge Graph | ✅ Accepted | 2026-02-15 | Architecture Board |
| ADR-0006 | Qdrant for Semantic Search | ✅ Accepted | 2026-02-15 | Architecture Board |
| ADR-0007 | Contract-First Development | ✅ Accepted | 2026-03-01 | Architecture Board |
| ADR-0008 | Multi-Tenancy Strategy | ✅ Accepted | 2026-03-01 | Architecture Board |

### Security

| ADR | Title | Status | Date | Owner |
|-----|-------|--------|------|-------|
| ADR-0010 | Authentication/Authorization/Session Split | ✅ Accepted | 2026-03-15 | Security Team |
| ADR-0011 | Audit Events Immutable | ✅ Accepted | 2026-03-15 | Security Team |
| ADR-0012 | No Raw SQL Outside Repositories | ✅ Accepted | 2026-03-15 | Security Team |

### Clinical

| ADR | Title | Status | Date | Owner |
|-----|-------|--------|------|-------|
| ADR-0020 | Clinical Decision Support as Supporting Domain | ✅ Accepted | 2026-04-01 | Clinical Team |
| ADR-0021 | Evidence Required for CDS | ✅ Accepted | 2026-04-01 | Clinical Team |
| ADR-0022 | Trust as Cross-Cutting Service | ✅ Accepted | 2026-04-15 | Clinical Team |

### Infrastructure

| ADR | Title | Status | Date | Owner |
|-----|-------|--------|------|-------|
| ADR-0030 | Kubernetes Deployment | ✅ Accepted | 2026-05-01 | Infrastructure |
| ADR-0031 | Prometheus + Grafana Observability | ✅ Accepted | 2026-05-01 | Infrastructure |
| ADR-0032 | Circuit Breaker Pattern | ✅ Accepted | 2026-05-15 | Infrastructure |

### Integration

| ADR | Title | Status | Date | Owner |
|-----|-------|--------|------|-------|
| ADR-0040 | FHIR R4 Integration | ✅ Accepted | 2026-06-01 | Integration Team |
| ADR-0041 | MQTT for Device Connectivity | ✅ Accepted | 2026-06-01 | Integration Team |
| ADR-0042 | External Integrations via Adapters | ✅ Accepted | 2026-06-15 | Integration Team |

---

## ADR Index by Status

### Accepted (Active)

| ADR | Title |
|-----|-------|
| ADR-0001 | Hexagonal Architecture |
| ADR-0002 | PostgreSQL as Primary Database |
| ADR-0003 | Event-Driven Architecture |
| ADR-0004 | Redis Cache-Aside Pattern |
| ADR-0005 | Neo4j for Knowledge Graph |
| ADR-0006 | Qdrant for Semantic Search |
| ADR-0007 | Contract-First Development |
| ADR-0008 | Multi-Tenancy Strategy |
| ADR-0010 | Authentication/Authorization/Session Split |
| ADR-0011 | Audit Events Immutable |
| ADR-0012 | No Raw SQL Outside Repositories |
| ADR-0020 | Clinical Decision Support as Supporting Domain |
| ADR-0021 | Evidence Required for CDS |
| ADR-0022 | Trust as Cross-Cutting Service |
| ADR-0030 | Kubernetes Deployment |
| ADR-0031 | Prometheus + Grafana Observability |
| ADR-0032 | Circuit Breaker Pattern |
| ADR-0040 | FHIR R4 Integration |
| ADR-0041 | MQTT for Device Connectivity |
| ADR-0042 | External Integrations via Adapters |

### Superseded

| ADR | Title | Superseded By |
|-----|-------|---------------|
| - | None yet | - |

### Deprecated

| ADR | Title | Reason |
|-----|-------|--------|
| - | None yet | - |

### Proposed

| ADR | Title | Status |
|-----|-------|--------|
| - | None | - |

---

## ADR Lifecycle

```
Proposed → Accepted → Superseded/Deprecated
    ↓
Any ADR can be updated or replaced.
All changes are versioned.
No ADR is permanent if evidence shows it should change.
```

---

## How to Add an ADR

1. Create file: `/docs/adr/ADR-XXXX_TITLE.md`
2. Fill template:
   ```markdown
   # ADR-XXXX: Title
   
   Status: Proposed
   
   ## Context
   ## Decision
   ## Consequences
   ```
3. Submit for Architecture Board review
4. Update this index when accepted

---

## Review Schedule

ADRs are reviewed quarterly:
- Q1 2026: January-March
- Q2 2026: April-June
- Q3 2026: July-September
- Q4 2026: October-December

---

*EREN ADR Index v1.0*
*Architecture Board - 2026-07-15*
