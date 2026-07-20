# EREN Epic 0-Infra — Infrastructure Design Documents
*Version 1.0 - 2026-07-16*

---

## Purpose

Epic 0-Infra fills the infrastructure gaps identified in Epic 0. While Epic 0 defined the **architectural vision** — what the system must do and why — Epic 0-Infra defines the **technical infrastructure** — how the system will be built and operated.

These documents are extensions of **Epic 0.5 (Advanced Architecture)** and must be read together with:
- `EREN_ARCHITECTURE_BLUEPRINT.md` (Epic 0)
- `EREN_EVENT_ARCHITECTURE.md` (Epic 0)
- `EREN_CONSISTENCY_MODEL.md` (Epic 0)
- `EREN_MULTITENANCY_STRATEGY.md` (Epic 0)
- `EREN_ARCHITECTURAL_GUARDRAILS.md` (Epic 0.2)
- `EREN_ADR_INDEX.md` (Epic 0.9 — REDIRECT)

They are **implemented by Epic 1 (Infrastructure Platform)** and **referenced by Epic 2-10**.

---

## Relationship to Epic 0

```
Epic 0 (Foundation)
├── Epic 0.1 (Correcciones)
├── Epic 0.2 (Guardrails)
├── Epic 0.5 (Advanced Architecture)
│   ├── EREN_EVENT_ARCHITECTURE.md ✓
│   ├── EREN_CONSISTENCY_MODEL.md ✓
│   ├── EREN_FAILURE_MODEL.md ✓
│   └── EREN_BOUNDED_CONTEXT_MAP.md ✓
└── Epic 0.9 (Operational)
    ├── EREN_ADR_INDEX.md ✓
    ├── EREN_UBIQUITOUS_LANGUAGE.md ✓
    └── ...

Epic 0-Infra (NEW — Extension of Epic 0.5)
├── EREN_INFRASTRUCTURE_BLUEPRINT.md
├── EREN_INFRASTRUCTURE_ADR_INDEX.md  ← REDIRECT to ../adr/
├── ../adr/epic0-infra/ADR-0080.md: Kubernetes
├── ../adr/epic0-infra/ADR-0081.md: Kafka
├── ../adr/epic0-infra/ADR-0082.md: S3/MinIO
├── ../adr/epic0-infra/ADR-0083.md: Outbox Pattern
├── ../adr/epic0-infra/ADR-0084.md: RLS in Alembic
├── ../adr/epic0-infra/ADR-0085.md: Observability Stack
├── ../adr/epic0-infra/ADR-0086.md: Backup/DR
├── ../adr/epic0-infra/ADR-0090.md: GitOps (Proposed)
├── ../adr/epic0-infra/ADR-0091.md: Service Mesh (Proposed)
├── ../adr/epic0-infra/ADR-0092.md: API Gateway (Proposed)
├── ../adr/epic0-infra/ADR-0093.md: Celery (**ACCEPTED**)
├── ../adr/epic0-infra/ADR-0094.md: Schema Registry (Proposed)
├── EREN_LOCAL_DEV_SETUP.md
├── EREN_OBSERVABILITY_SETUP.md
├── EREN_SETTINGS_MODEL.md
└── EREN_RUNBOOKS.md
```

---

## Document Index

| Document | Purpose | Status |
|----------|---------|--------|
| [EREN_INFRASTRUCTURE_BLUEPRINT.md](./EREN_INFRASTRUCTURE_BLUEPRINT.md) | Complete infrastructure stack definition | READY |
| [EREN_INFRASTRUCTURE_ADR_INDEX.md](./EREN_INFRASTRUCTURE_ADR_INDEX.md) | REDIRECT to [`../adr/epic0-infra/`](../adr/epic0-infra/) | REDIRECT |
| [ADR-0080.md](../adr/epic0-infra/ADR-0080.md) | K8s as deployment platform decision | ACCEPTED |
| [ADR-0081.md](../adr/epic0-infra/ADR-0081.md) | Kafka as Primary Message Broker | ACCEPTED |
| [ADR-0082.md](../adr/epic0-infra/ADR-0082.md) | S3/MinIO strategy | ACCEPTED |
| [ADR-0083.md](../adr/epic0-infra/ADR-0083.md) | Outbox pattern specification | ACCEPTED |
| [ADR-0084.md](../adr/epic0-infra/ADR-0084.md) | Row-Level Security in Alembic | ACCEPTED |
| [ADR-0085.md](../adr/epic0-infra/ADR-0085.md) | Prometheus/Grafana/Jaeger/Loki | ACCEPTED |
| [ADR-0086.md](../adr/epic0-infra/ADR-0086.md) | Backup and DR strategy | ACCEPTED |
| [ADR-0090.md](../adr/epic0-infra/ADR-0090.md) | GitOps with ArgoCD | PROPOSED |
| [ADR-0091.md](../adr/epic0-infra/ADR-0091.md) | Service Mesh (Istio vs Linkerd) | PROPOSED |
| [ADR-0092.md](../adr/epic0-infra/ADR-0092.md) | API Gateway Strategy | PROPOSED |
| [ADR-0093.md](../adr/epic0-infra/ADR-0093.md) | Celery as Task Queue | **ACCEPTED ✅** |
| [ADR-0094.md](../adr/epic0-infra/ADR-0094.md) | Schema Registry Strategy | PROPOSED |
| [EREN_LOCAL_DEV_SETUP.md](./EREN_LOCAL_DEV_SETUP.md) | Local development environment | READY |
| [EREN_OBSERVABILITY_SETUP.md](./EREN_OBSERVABILITY_SETUP.md) | Observability setup guide | READY |
| [EREN_SETTINGS_MODEL.md](./EREN_SETTINGS_MODEL.md) | Settings/configuration model | READY |
| [EREN_RUNBOOKS.md](./EREN_RUNBOOKS.md) | Operational runbooks | READY |

---

## Gap Analysis

This documentation addresses the following gaps identified in Epic 0:

| Gap | Document |
|-----|---------|
| Kubernetes deployment not specified | [`../adr/epic0-infra/ADR-0080.md`](../adr/epic0-infra/ADR-0080.md) |
| Message queue choice not documented | [`../adr/epic0-infra/ADR-0081.md`](../adr/epic0-infra/ADR-0081.md) |
| S3/MinIO storage strategy missing | [`../adr/epic0-infra/ADR-0082.md`](../adr/epic0-infra/ADR-0082.md) |
| Outbox pattern undefined | [`../adr/epic0-infra/ADR-0083.md`](../adr/epic0-infra/ADR-0083.md) |
| RLS implementation not guided | [`../adr/epic0-infra/ADR-0084.md`](../adr/epic0-infra/ADR-0084.md) |
| Observability stack incomplete | [`../adr/epic0-infra/ADR-0085.md`](../adr/epic0-infra/ADR-0085.md) |
| Backup/DR not specified | [`../adr/epic0-infra/ADR-0086.md`](../adr/epic0-infra/ADR-0086.md) |
| API Gateway not defined | [`../adr/epic0-infra/ADR-0092.md`](../adr/epic0-infra/ADR-0092.md) |
| Task Queue defined | [`../adr/epic0-infra/ADR-0093.md`](../adr/epic0-infra/ADR-0093.md) | **ACCEPTED** (Epic 1 implemented) |
| Schema Registry not defined | [`../adr/epic0-infra/ADR-0094.md`](../adr/epic0-infra/ADR-0094.md) |
| No local dev setup | `EREN_LOCAL_DEV_SETUP.md` |
| No observability setup guide | `EREN_OBSERVABILITY_SETUP.md` |
| Settings model unclear | `EREN_SETTINGS_MODEL.md` |
| No operational runbooks | `EREN_RUNBOOKS.md` |

---

## Architecture Decision Status

All ADRs are located at [`../adr/epic0-infra/`](../adr/epic0-infra/).

| ADR | Title | Status | Date | Owner |
|-----|-------|--------|------|-------|
| [ADR-0080](../adr/epic0-infra/ADR-0080.md) | Kubernetes as Deployment Platform | ACCEPTED | 2026-07-16 | Infrastructure Team |
| [ADR-0081](../adr/epic0-infra/ADR-0081.md) | Kafka as Primary Message Broker | ACCEPTED | 2026-07-16 | Infrastructure Team |
| [ADR-0082](../adr/epic0-infra/ADR-0082.md) | S3/MinIO Object Storage Strategy | ACCEPTED | 2026-07-16 | Infrastructure Team |
| [ADR-0083](../adr/epic0-infra/ADR-0083.md) | Outbox Pattern for Event Publishing | ACCEPTED | 2026-07-16 | Architecture Board |
| [ADR-0084](../adr/epic0-infra/ADR-0084.md) | Row-Level Security in Alembic Migrations | ACCEPTED | 2026-07-16 | Architecture Board |
| [ADR-0085](../adr/epic0-infra/ADR-0085.md) | Observability Stack | ACCEPTED | 2026-07-16 | Infrastructure Team |
| [ADR-0086](../adr/epic0-infra/ADR-0086.md) | Backup and Disaster Recovery Strategy | ACCEPTED | 2026-07-16 | Infrastructure Team |
| [ADR-0090](../adr/epic0-infra/ADR-0090.md) | GitOps with ArgoCD | PROPOSED | 2026-07-16 | Infrastructure Team |
| [ADR-0091](../adr/epic0-infra/ADR-0091.md) | Service Mesh (Istio vs Linkerd) | PROPOSED | 2026-07-16 | Infrastructure Team |
| [ADR-0092](../adr/epic0-infra/ADR-0092.md) | API Gateway Strategy | PROPOSED | 2026-07-16 | Infrastructure Team |
| [ADR-0093](../adr/epic0-infra/ADR-0093.md) | Celery as Task Queue | Accepted | 2026-07-16 | Infrastructure Team |
| [ADR-0094](../adr/epic0-infra/ADR-0094.md) | Schema Registry Strategy | PROPOSED | 2026-07-16 | Infrastructure Team |

See full ADR index at [`../adr/README.md`](../adr/README.md).

---

## Epic 0-Infra Complete — Ready for Epic 4

**Epic 0-Infra Status:** COMPLETE ✅ v1.0

**EPIC Roadmap Status:**
- EPIC 0 (Architecture) — COMPLETE ✅
- EPIC 0-Infra (Infrastructure Design) — COMPLETE ✅
- EPIC 1 (Infrastructure Platform) — COMPLETE ✅ (merged)
- EPIC 2 (Core Business Domain) — COMPLETE ✅ (merged)
- EPIC 3 (Hospital Management) — COMPLETE ✅ (merged PR #131)
- **EPIC 4 (AI Core) — IN PROGRESS 🚧**
- EPIC 5 (Clinical Intelligence) — Pending

All infrastructure design decisions are now documented and ready for Epic 4 implementation.

**Score:** Pre-implementation (will be evaluated after Epic 4)

**Epic Dependencies:**

```
Epic 0-Infra ────────────────────────────────────────────→ Epic 1
  │                                                              │
  ├── Kubernetes ADR ────────────────────────→ K8s manifests + Helm │
  ├── Kafka ADR ──────────────────────────→ RabbitMQ messaging    │
  ├── S3/MinIO ADR ────────────────────→ Object storage          │
  ├── Outbox ADR ────────────────────────→ Outbox worker script   │
  ├── RLS ADR ────────────────────────────→ Alembic RLS migration│
  ├── Observability ADR ─────────────────→ OTel + Grafana alerts │
  ├── Celery ADR ────────────────────────→ Celery task queue    │
  └── Backup/DR ADR ────────────────────→ K8s PVC + CronJob      │

Epic 4 ────────────────────────────────────────────────→ Epic 5
  │                                                              │
  ├── FastAPI + observability ─────────────→ AI Core platform      │
  └── Redis ─────────────────────────────→ Session memory        │
```

**Next:** Epic 4 - AI Core 🚧 (see [`../epic4/README.md`](../epic4/README.md))

**These are LIVE documents:**
- All are versioned
- All are reviewed before Epic implementation
- All can be updated when evidence requires
