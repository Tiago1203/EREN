# EREN Architecture Decision Records (ADR)

---

## Overview

This is the **master index** for all Architecture Decision Records in EREN. ADRs are organized by **EPIC** — each EPIC gets its own folder.

```
docs/adr/
├── README.md                        ← This file (master index)
├── epic0/                          ← Foundation decisions
├── epic0-infra/                    ← Infrastructure decisions
├── epic1/                          ← EPIC 1 decisions (Infrastructure Platform)
├── epic2/                          ← EPIC 2 decisions (Core Business Domain)
├── epic3/                          ← EPIC 3 decisions (Hospital Management)
├── epic4/                          ← EPIC 4 decisions (AI Core)
├── epic5/                          ← EPIC 5 decisions (Clinical Intelligence)
├── epic6/                          ← EPIC 6 decisions (Integrations)
├── epic7/                          ← EPIC 7 decisions (User Experience)
├── epic8/                          ← EPIC 8 decisions (Production Readiness)
├── epic9/                          ← EPIC 9 decisions (Machine Learning)
├── epic10/                         ← EPIC 10 decisions (Enterprise Release)
└── _archive/                       ← Old/outdated ADRs (historical reference)
```

---

## ADR Count by EPIC

| EPIC | Accepted | Proposed | Deprecated | Total |
|------|----------|----------|------------|--------|
| Epic 0 | 24 | 6 | 2 | 32 |
| Epic 0-Infra | 7 | 3 | 0 | 10 |
| **Epic 1** | **11** | **0** | **0** | **11** |
| Epic 2-10 | 0 | 0 | 0 | 0 |
| **Total** | **42** | **9** | **2** | **53** |

---

## ADR Status Definitions

| Status | Meaning |
|--------|---------|
| **Proposed** | Under review, not yet accepted |
| **Accepted** | Approved and in effect |
| **Superseded** | Replaced by a newer ADR |
| **Deprecated** | No longer relevant |

**Rule:** No architectural decision without an ADR. No ADR without a status.

---

## ADR Numbering Conventions

```
ADR-0001 to ADR-0099  →  Epic 0 (Foundation)
ADR-0100 to ADR-0199  →  Epic 1 (Infrastructure Platform)
ADR-0200 to ADR-0299  →  Epic 2 (Core Business Domain)
ADR-0300 to ADR-0399  →  Epic 3 (Hospital Management)
ADR-0400 to ADR-0499  →  Epic 4 (AI Core)
ADR-0500 to ADR-0599  →  Epic 5 (Clinical Intelligence)
ADR-0600 to ADR-0699  →  Epic 6 (Integrations)
ADR-0700 to ADR-0799  →  Epic 7 (User Experience)
ADR-0800 to ADR-0899  →  Epic 8 (Production Readiness)
ADR-0900 to ADR-0999  →  Epic 9 (Machine Learning)
ADR-1000 to ADR-1099  →  Epic 10 (Enterprise Release)
```

**Note:** Epic 0 ADRs use the original numbering from the legacy ADR index (ADR-0001 to ADR-0076) to preserve history. Epic 0-Infra ADRs start at ADR-0080.

---

## Quick Reference

### Epic 0 — Foundation

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0001 | Hexagonal Architecture | Accepted |
| ADR-0002 | PostgreSQL as Primary Database | Accepted |
| ADR-0003 | Event-Driven Architecture | Accepted |
| ADR-0004 | Redis Cache-Aside Pattern | Accepted |
| ADR-0005 | Neo4j for Knowledge Graph | Accepted |
| ADR-0006 | Qdrant for Semantic Search | Accepted |
| ADR-0007 | Contract-First Development | Accepted |
| ADR-0008 | Multi-Tenancy Strategy | Accepted |
| ADR-0010 | Authentication/Authorization/Session Split | Accepted |
| ADR-0011 | Audit Events Immutable | Accepted |
| ADR-0012 | No Raw SQL Outside Repositories | Accepted |
| ADR-0020 | Clinical Decision Support as Supporting Domain | Accepted |
| ADR-0021 | Evidence Required for CDS | Accepted |
| ADR-0022 | Trust as Cross-Cutting Service | Accepted |
| ADR-0030 | Kubernetes Deployment | Accepted |
| ADR-0031 | Prometheus + Grafana Observability | Accepted |
| ADR-0032 | Circuit Breaker Pattern | Deprecated |
| ADR-0040 | FHIR R4 Integration | Accepted |
| ADR-0041 | MQTT for Device Connectivity | Accepted |
| ADR-0042 | External Integrations via Adapters | Deprecated |
| ADR-0043 | DICOM Integration | Accepted |
| ADR-0044 | HL7 V2/V3 Integration | Accepted |
| ADR-0045 | Medical Device Vendor Adapters | Accepted |
| ADR-0050 | Hospital Context Architecture | Accepted |
| ADR-0051 | Organization Multi-Campus Strategy | Accepted |
| ADR-0052 | Department Hierarchy Model | Accepted |
| ADR-0055 | AI Core Architecture | Accepted |
| ADR-0056 | Cognitive Capability Contracts | Accepted |
| ADR-0057 | LLM Provider Abstraction | Accepted |
| ADR-0060 | Clinical Intelligence Context Architecture | Accepted |
| ADR-0061 | CDS Evidence Requirements | Accepted |
| ADR-0062 | AI Explainability Requirements | Accepted |
| ADR-0065 | Web Frontend Architecture | Proposed |
| ADR-0066 | Mobile App Architecture | Proposed |
| ADR-0070 | GDPR Compliance Strategy | Proposed |
| ADR-0071 | ISO 27001 Compliance | Proposed |
| ADR-0075 | ML Feedback Loop Architecture | Proposed |
| ADR-0076 | Model Versioning Strategy | Proposed |

### Epic 0-Infra — Infrastructure

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0080 | Kubernetes as Deployment Platform | Accepted |
| ADR-0081 | Kafka as Primary Message Broker | Accepted |
| ADR-0082 | S3/MinIO Object Storage Strategy | Accepted |
| ADR-0083 | Outbox Pattern for Event Publishing | Accepted |
| ADR-0084 | Row-Level Security in Alembic Migrations | Accepted |
| ADR-0085 | Observability Stack | Accepted |
| ADR-0086 | Backup and Disaster Recovery Strategy | Accepted |
| ADR-0090 | GitOps with ArgoCD | Proposed |
| ADR-0091 | Service Mesh (Istio vs Linkerd) | Proposed |
| ADR-0092 | API Gateway Strategy | Proposed |
| ADR-0093 | Celery as Task Queue | Proposed |
| ADR-0094 | Schema Registry Strategy | Proposed |

### Epic 1-10 — Pending

| EPIC | Status |
|------|--------|
| Epic 1 (Infrastructure Platform) | **COMPLETE ✅** |
| Epic 2 (Core Business Domain) | Pending |
| Epic 3 (Hospital Management) | Pending |
| Epic 4 (AI Core) | Pending |
| Epic 5 (Clinical Intelligence) | Pending |
| Epic 6 (Integrations) | Pending |
| Epic 7 (User Experience) | Pending |
| Epic 8 (Production Readiness) | Pending |
| Epic 9 (Machine Learning) | Pending |
| Epic 10 (Enterprise Release) | Pending |

---

## How to Add an ADR

1. Create file: `docs/adr/epic{N}/ADR-XXXX_TITLE.md`
2. Use the standard template
3. Submit for Architecture Board review
4. Update this index

### ADR Template

```markdown
# ADR-XXXX: Title

**Status:** Proposed | Accepted | Superseded | Deprecated

**Date:** YYYY-MM-DD

**Deciders:** Team

---

## Context
(What problem are we solving?)

## Decision
(What we decided to do?)

## Reasons
(Why this decision?)

## Consequences
### Positive
### Negative

---

*ADR-XXXX - YYYY-MM-DD*
```

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

## Review Schedule

ADRs are reviewed quarterly:
- Q1: January-March
- Q2: April-June
- Q3: July-September
- Q4: October-December

---

## Deprecations

| ADR | Deprecated By | Reason |
|-----|-------------|--------|
| ADR-0032 (Circuit Breaker Pattern) | — | Standard pattern, not a specific architectural decision — lives in Failure Model |
| ADR-0042 (External Integrations via Adapters) | — | Redundant with ADR-0040, ADR-0041, ADR-0043, ADR-0044, ADR-0045 |

---

*EREN ADR Master Index v1.0*
*Architecture Board - 2026-07-16*
