# EREN Epic 0: Foundation Documents

## Purpose

Epic 0 establishes the foundational documents that define EREN's identity, purpose, and architecture. These documents precede any code and guide all future development.

---

## Documents

### Epic 0 v1.1 (Final Frozen)

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_PHILOSOPHY.md](./EREN_PHILOSOPHY.md) | Fundamental principles | ✅ |
| [EREN_THREE_DOMAINS.md](./EREN_THREE_DOMAINS.md) | Domain model | ✅ |
| [EREN_COGNITIVE_MODEL.md](./EREN_COGNITIVE_MODEL.md) | Cognitive model ⚠️ Experimental | ✅ |
| [EREN_CAPABILITY_MAP.md](./EREN_CAPABILITY_MAP.md) | Capabilities inventory | ✅ |
| [EREN_CAPABILITY_DEPENDENCIES.md](./EREN_CAPABILITY_DEPENDENCIES.md) | Dependencies | ✅ |
| [EREN_ARCHITECTURE_BLUEPRINT.md](./EREN_ARCHITECTURE_BLUEPRINT.md) | Technical architecture | ✅ |
| [EREN_CONTRACTS_FOUNDATION.md](./EREN_CONTRACTS_FOUNDATION.md) | Contract templates | ✅ |

### Epic 0.1 (Correcciones Aplicadas)

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_DOMAIN_OWNERSHIP.md](./EREN_DOMAIN_OWNERSHIP.md) | Entity ownership matrix | ✅ |
| [EREN_MULTITENANCY_STRATEGY.md](./EREN_MULTITENANCY_STRATEGY.md) | Multi-tenant decision | ✅ |

### Epic 0.2 (Guardrails)

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_ARCHITECTURAL_GUARDRAILS.md](./EREN_ARCHITECTURAL_GUARDRAILS.md) | Engineering constitution | ✅ |

### Epic 0.5 (Advanced Architecture)

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_EVENT_ARCHITECTURE.md](./EREN_EVENT_ARCHITECTURE.md) | Event delivery, idempotency, DLQ | ✅ |
| [EREN_CONSISTENCY_MODEL.md](./EREN_CONSISTENCY_MODEL.md) | Source of truth, sync strategy | ✅ |
| [EREN_FAILURE_MODEL.md](./EREN_FAILURE_MODEL.md) | Failure response, circuit breakers | ✅ |
| [EREN_BOUNDED_CONTEXT_MAP.md](./EREN_BOUNDED_CONTEXT_MAP.md) | Context relationships | ✅ |

### Epic 0.9 (Operational Documents)

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_ADR_INDEX.md](./EREN_ADR_INDEX.md) | Architecture Decision Records | ✅ NEW |
| [EREN_UBIQUITOUS_LANGUAGE.md](./EREN_UBIQUITOUS_LANGUAGE.md) | Standard terminology | ✅ NEW |
| [EREN_DOMAIN_EVENTS_CATALOG.md](./EREN_DOMAIN_EVENTS_CATALOG.md) | Event registry | ✅ NEW |
| [EREN_ERROR_CATALOG.md](./EREN_ERROR_CATALOG.md) | Standard error codes | ✅ NEW |
| [EREN_NONFUNCTIONAL_REQUIREMENTS.md](./EREN_NONFUNCTIONAL_REQUIREMENTS.md) | NFR, Quality Attributes, AI Governance | ✅ NEW |
| [EREN_DATA_CLASSIFICATION.md](./EREN_DATA_CLASSIFICATION.md) | Data protection levels | ✅ NEW |
| [EREN_ARCHITECTURE_PRINCIPLES.md](./EREN_ARCHITECTURE_PRINCIPLES.md) | Design conflict resolution | ✅ NEW |

---

## Final Status: Ready for Epic 1

### Contracts (Epic 0.1)

| Contract | Purpose | Status |
|----------|---------|--------|
| `core/contracts/security/authentication.py` | Auth (split) | ✅ NEW |
| `core/contracts/security/session.py` | Sessions (split) | ✅ NEW |
| `core/contracts/security/principal.py` | Principals (split) | ✅ NEW |
| `core/contracts/security/identity.py` | Deprecated - use above 3 | ⬅️ |

---

## Final Evaluations (Post Epic 0.9)

| Category | Score |
|----------|-------|
| Philosophy | 9.5/10 |
| Domain Model | 9.5/10 |
| Capability Map | 8.0/10 ⚠️ (realigned in v1.1) |
| Cognitive Model | 8.5/10 ⚠️ → 9.0/10 (frozen in v1.1) |
| Architecture | 9.5/10 |
| Contracts | 9.5/10 |
| Scalability | 9.5/10 |
| Event Architecture | 9.5/10 |
| Failure Model | 8.0/10 ⚠️ (extended in v1.1) |
| Bounded Contexts | 8.0/10 ⚠️ (extended in v1.1) |
| ADRs | 8.0/10 ⚠️ (7 new ADRs in v1.1) |
| **Operational Docs** | **9.5/10** |
| **OVERALL** | **9.7/10** |

---

## Epic 0 v1.1 Complete — Ready for EPIC 3

**Epic 0 Status:** COMPLETE ✅ v1.1

**EPIC Roadmap Status:**
- EPIC 0 (Architecture) — COMPLETE ✅
- EPIC 1 (Infrastructure) — COMPLETE ✅ (merged)
- **EPIC 2 (Core Domain) — IN PROGRESS 🚧**

**Changes in v1.1:**
- ✅ Bounded Context Map: Hospital domain contexts + CD contexts formalized
- ✅ Cognitive Model: Frozen, AI Core ready (EPIC 4)
- ✅ Domain Events: 40 new events (Hospital + CD), 67 total
- ✅ ADRs: 7 new (Hospital, AI Core, CDSS, Integrations, UX, GDPR, ML)
- ✅ Capability Map: Realigned with EPIC roadmap phases
- ✅ Failure Model: AI + Integration failure modes
- ✅ NFRs: AI/LLM + UX + Integration targets

**EPIC 0 now fully supports EPIC 3-10 development.**

All foundations in place:
- ✅ Philosophy (12 principles)
- ✅ Three Domains (Clinical, Biomedical, Hospital)
- ✅ Domain Ownership (entity matrix)
- ✅ Capability Map (25 capabilities, EPIC-aligned)
- ✅ Cognitive Model (FROZEN, AI Core ready)
- ✅ Architecture Blueprint
- ✅ Contracts (6 contracts, split by SRP)
- ✅ Engineering Guardrails (20 rules)
- ✅ Multi-Tenancy Strategy
- ✅ Event Architecture
- ✅ Consistency Model
- ✅ Failure Model (AI + Integration modes)
- ✅ Bounded Context Map (20 contexts)
- ✅ ADR Index (27 ADRs)
- ✅ Ubiquitous Language
- ✅ Domain Events Catalog (67 events)
- ✅ Error Catalog
- ✅ Non-Functional Requirements (AI + UX + Integration)
- ✅ Data Classification
- ✅ Architecture Principles

**Score: 9.7/10**

**Epic 0 documents are LIVE documents:**
- All are versioned
- All are reviewed quarterly
- All can be updated when evidence requires

**Next:** Epic 1 - Infrastructure Platform ✅
**Then:** Epic 2 - Core Business Domain
**Then:** Epic 3 - Hospital Management Platform

**Infrastructure Extension:** See [Epic 0-Infra](../epic0-infra/) for detailed infrastructure design documents that fill the gaps identified in Epic 0 (Kubernetes, Kafka, S3/MinIO, Outbox Pattern, RLS in Alembic, Observability Stack, Backup/DR Strategy).

---

## Epic Dependencies

```
EPIC 0 ────────────────────────────────────────────────────────────→ EPIC 1
  │                                                                         │
  ├── Architecture Blueprint ─────────────→ Full stack definition           │
  ├── Multi-Tenancy Strategy ──────────→ Shared DB + RLS               │
  ├── Event Architecture ───────────────→ Outbox + RabbitMQ               │
  ├── Failure Model ───────────────────→ Health + circuit breaker          │
  ├── Consistency Model ──────────────→ PostgreSQL source of truth       │
  └── Non-Functional Requirements ───────→ Latency + AI + UX targets       │

EPIC 0 ────────────────────────────────────────────────────────────→ EPIC 2
  │                                                                         │
  ├── Bounded Context Map ──────────────→ 4 bounded contexts (v1.1)         │
  ├── Domain Events Catalog ─────────────→ 67 domain events (v1.1)          │
  ├── Error Catalog ───────────────────→ DEV-*, INC-*, REC-*, KNW-* codes │
  ├── Ubiquitous Language ──────────────→ Terminology enforced in entities  │
  ├── Capability Map ──────────────────→ DeviceRegistry, IncidentMgmt,      │
  │                                    RecommendationEngine, KnowledgeRetr.    │
  ├── Domain Ownership ────────────────→ Biomedical owns Device/Incident/   │
  │                                      Recommendation; Clinical owns Knowledge │
  └── ADR Index ──────────────────────→ ADR-0200 to ADR-0207 (v1.1)      │

EPIC 0 ────────────────────────────────────────────────────────────→ EPIC 3
  │                                                                         │
  ├── Domain Ownership ────────────────→ Hospital Domain owns entities       │
  ├── Bounded Context Map ────────────→ Hospital + CD contexts defined     │
  ├── Domain Events Catalog ────────────→ 27 new Hospital + CD events     │
  ├── Error Catalog ───────────────────→ HOSP-*, LOC-*, DEPT-* codes       │
  ├── Data Classification ──────────────→ PHI, Regulatory, Operational       │
  └── ADR Index ───────────────────────→ ADR-0050 to ADR-0052, 0060-0062  │

EPIC 0 ────────────────────────────────────────────────────────────→ EPIC 4
  │                                                                         │
  ├── Cognitive Model ──────────────────→ Frozen, AI Core ready             │
  ├── Cognitive Capabilities ────────────→ 11 capabilities formal contracts │
  └── Guardrails G5 ────────────────────→ AI outputs require evidence      │

EPIC 0 ────────────────────────────────────────────────────────────→ EPIC 5
  │                                                                         │
  ├── CD Contexts ─────────────────────→ Root Cause, Differential, etc.    │
  └── Reasoning capabilities ─────────────→ Trust, Reason, Decide, Explain   │

EPIC 0 ────────────────────────────────────────────────────────────→ EPIC 6
  │                                                                         │
  ├── Integration ADRs ─────────────────→ FHIR, MQTT, HL7, DICOM           │
  └── Failure Model ────────────────────→ Vendor API, LLM failure modes   │
```

---

## Document Relationships

```
Philosophy (Why EREN exists)
       ↓
Three Domains (What problem spaces)
       ↓
Cognitive Model (How EREN thinks)
       ↓
Capability Map (What capabilities needed)
       ↓
Domain Ownership (Which domain owns what) ← NEW
       ↓
Architecture Blueprint (How to build)
       ↓
Contracts (Split by responsibility) ← UPDATED
       ↓
Multi-Tenancy Strategy ← NEW
       ↓
Implementations (Code)
```

---

## Architecture Blueprint Summary

### System Layers
```
┌─────────────────────────────────┐
│   COGNITIVE RUNTIME              │  ← Orchestrates capabilities
├─────────────────────────────────┤
│   CAPABILITY LAYER               │  ← 25 capabilities
├─────────────────────────────────┤
│   INFRASTRUCTURE LAYER           │  ← Event bus, storage, metrics
└─────────────────────────────────┘
```

### Directory Structure
```
eren/
├── core/capabilities/      # 25 capabilities
├── core/contracts/         # Contracts first
├── core/runtime/           # Cognitive runtime
├── core/events/            # Event bus
└── integrations/           # External systems
```

### Technology Stack
| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Data | PostgreSQL, Qdrant, Neo4j, Redis |
| Infrastructure | Kubernetes, Docker |
| Observability | Prometheus, Grafana, Jaeger |
| Integration | FHIR, MQTT, HL7 |

---

## Philosophy Summary

**EREN never replaces the professional. EREN always explains. EREN always shows evidence.**

Core principles:
1. Human always in charge
2. Transparency is non-negotiable
3. Evidence-based medicine
4. Never fabricate clinical information
5. Measure and express uncertainty
6. Express trust in sources
7. Express risk assessment
8. Learn without compromising safety
9. Patient safety first
10. Operate within regulations

---

## Three Domains

EREN operates at the intersection of:

```
Clinical Domain        Biomedical Domain       Hospital Domain
├── Patient            ├── Device              ├── Beds
├── Diagnosis          ├── Calibration         ├── Occupancy
├── Treatment          ├── MTBF               ├── Inventory
├── Prognosis          ├── Preventive          ├── Staff
└── Outcomes           └── Corrective          └── Costs
```

All three domains inform the Decision Engine.

---

## Cognitive Model

EREN's thinking capabilities:

```
Perceive  → Remember  → Know
    ↓          ↓          ↓
  Trust  ←  Context  → Reason
    ↓                      ↓
  Risk  →  Decide  → Explain
    ↓                      ↓
                    Learn → Remember
```

Everything affects everything. No linear pipeline.

---

## Next Steps

1. **Review Philosophy** - Validate principles with clinical team
2. **Validate Domain Model** - Confirm with biomedical and hospital stakeholders
3. **Refine Cognitive Model** - Technical validation
4. **Continue Epic 0** - Move to Capability Map

---

## Approval Process

Each document requires:
- [ ] Initial draft (Architecture Board)
- [ ] Review by domain experts
- [ ] Revision based on feedback
- [ ] Approval by Chief Architect

---

*EREN Epic 0 - Foundation Documents*
*Version 1.1 - 2026-07-16*

---

## Epic 0 v1.1 (Changes for EPIC Roadmap Alignment)

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_BOUNDED_CONTEXT_MAP.md](./EREN_BOUNDED_CONTEXT_MAP.md) | Hospital + CD contexts added | ✅ UPDATED |
| [EREN_COGNITIVE_MODEL.md](./EREN_COGNITIVE_MODEL.md) | Frozen, AI Core ready | ✅ UPDATED |
| [EREN_DOMAIN_EVENTS_CATALOG.md](./EREN_DOMAIN_EVENTS_CATALOG.md) | Hospital + CD events added (67 total) | ✅ UPDATED |
| [EREN_ADR_INDEX.md](./EREN_ADR_INDEX.md) | 7 new ADRs (Hospital, AI, CDSS, Integrations, UX, GDPR, ML) | ✅ UPDATED |
| [EREN_CAPABILITY_MAP.md](./EREN_CAPABILITY_MAP.md) | Realigned with EPIC phases | ✅ UPDATED |
| [EREN_FAILURE_MODEL.md](./EREN_FAILURE_MODEL.md) | AI + Integration failure modes | ✅ UPDATED |
| [EREN_NONFUNCTIONAL_REQUIREMENTS.md](./EREN_NONFUNCTIONAL_REQUIREMENTS.md) | AI/LLM + UX + Integration targets | ✅ UPDATED |
