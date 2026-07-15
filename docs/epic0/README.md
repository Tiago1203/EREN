# EREN Epic 0: Foundation Documents

## Purpose

Epic 0 establishes the foundational documents that define EREN's identity, purpose, and architecture. These documents precede any code and guide all future development.

---

## Documents

### Epic 0 v1.0 (Architecture Frozen)

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_PHILOSOPHY.md](./EREN_PHILOSOPHY.md) | Fundamental principles | ✅ |
| [EREN_THREE_DOMAINS.md](./EREN_THREE_DOMAINS.md) | Domain model | ✅ |
| [EREN_COGNITIVE_MODEL.md](./EREN_COGNITIVE_MODEL.md) | Cognitive model | ✅ |
| [EREN_CAPABILITY_MAP.md](./EREN_CAPABILITY_MAP.md) | Capabilities inventory | ✅ |
| [EREN_CAPABILITY_DEPENDENCIES.md](./EREN_CAPABILITY_DEPENDENCIES.md) | Dependencies | ✅ |
| [EREN_ARCHITECTURE_BLUEPRINT.md](./EREN_ARCHITECTURE_BLUEPRINT.md) | Technical architecture | ✅ |
| [EREN_CONTRACTS_FOUNDATION.md](./EREN_CONTRACTS_FOUNDATION.md) | Contract templates | ✅ |

### Epic 0.1 (Correcciones)

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_DOMAIN_OWNERSHIP.md](./EREN_DOMAIN_OWNERSHIP.md) | Entity ownership matrix | ✅ NEW |
| [EREN_MULTITENANCY_STRATEGY.md](./EREN_MULTITENANCY_STRATEGY.md) | Multi-tenant decision | ✅ NEW |

### Contracts (Epic 0.1)

| Contract | Purpose | Status |
|----------|---------|--------|
| `core/contracts/security/authentication.py` | Auth (split) | ✅ NEW |
| `core/contracts/security/session.py` | Sessions (split) | ✅ NEW |
| `core/contracts/security/principal.py` | Principals (split) | ✅ NEW |
| `core/contracts/security/identity.py` | Deprecated - use above 3 | ⬅️ |

---

## Epic 0.1 Changes (High Priority Fixes)

### 1. Domain Ownership ✅
- Every entity has single owner domain
- Clear ownership matrix documented

### 2. Identity Split ✅
- AuthenticationProvider (auth only)
- SessionProvider (sessions only)
- PrincipalProvider (identity data only)

### 3. Audit Immutability ✅
- Added immutability guarantee to contract
- Added verify_integrity() method
- Added verify_chain_integrity() method

### 4. Multi-Tenancy Strategy ✅
- Decision: Shared database + tenant_id
- RLS + application enforcement
- Scalability considerations

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
*Version 1.0 - 2026-07-15*
