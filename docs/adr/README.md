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
| Epic 0 | 30 | 6 | 2 | 38 |
| Epic 0-Infra | 8 | 4 | 0 | 12 |
| Epic 1 | 11 | 0 | 0 | 11 |
| Epic 2 | 6 | 2 | 0 | 8 |
| Epic 3 | 12 | 0 | 0 | 12 | ✅ All Accepted |
| **Epic 4** | **0** | **11** | **0** | **11** |
| Epic 5-10 | 0 | 0 | 0 | 0 |
| **Total** | **67** | **33** | **2** | **102** |

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

**Note:** Epic 0 ADRs use the original numbering from the legacy ADR index (ADR-0001 to ADR-0076) to preserve history. Epic 0-Infra ADRs start at ADR-0080. Epic 1 ADRs start at ADR-0100 (ADR-0100 reserved as gap).

---

## Quick Reference

### Epic 0 — Foundation (38 ADRs)

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

### Epic 1 — Infrastructure Platform (COMPLETE ✅)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0101 | FastAPI as API Framework | Accepted |
| ADR-0102 | SQLAlchemy 2.0 ORM + Alembic | Accepted |
| ADR-0103 | Repository Pattern Implementation | Accepted |
| ADR-0104 | Unit of Work Pattern | Accepted |
| ADR-0105 | Outbox Pattern for Reliable Events | Accepted |
| ADR-0106 | Redis Cache Strategy | Accepted |
| ADR-0107 | RabbitMQ Messaging | Accepted |
| ADR-0108 | OpenTelemetry Observability | Accepted |
| ADR-0109 | Structured Logging | Accepted |
| ADR-0110 | Health Check Strategy | Accepted |

### Epic 2 — Core Business Domain (COMPLETE ✅)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0200 | Domain Model Architecture | Accepted |
| ADR-0201 | Bounded Context Definitions | Accepted |
| ADR-0202 | Incident Sub-Aggregate (Investigation) | Accepted |
| ADR-0203 | Context Integration Pattern | Accepted |
| ADR-0204 | WorkOrder in Incident Bounded Context | Proposed |
| ADR-0205 | Knowledge Domain Isolation | Proposed |
| ADR-0206 | Patient and Diagnosis Scope — Not EPIC 2 | Accepted |
| ADR-0207 | Knowledge Article Value Objects | Accepted |

### Epic 3 — Hospital Management Platform (COMPLETE ✅)

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

### Epic 4 — AI Core (IN PROGRESS 🚧)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0400 | AI Core Architecture | Proposed |
| ADR-0401 | LLM Provider Abstraction | Proposed |
| ADR-0402 | Cognitive Runtime Design | Proposed |
| ADR-0403 | RAG Architecture | Proposed |
| ADR-0404 | Conversation Model | Proposed |
| ADR-0405 | Reasoning Engine Strategy | Proposed |
| ADR-0406 | Confidence Scoring Model | Proposed |
| ADR-0407 | Safety & Hallucination Detection | Proposed |
| ADR-0408 | Tool Orchestration | Proposed |
| ADR-0409 | Memory Architecture | Proposed |
| ADR-0410 | Explainability Requirements | Proposed |

### Epic 5-10 — Pending

| EPIC | Status |
|------|--------|
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

*EREN ADR Master Index v1.2*
*Architecture Board - 2026-07-20*
