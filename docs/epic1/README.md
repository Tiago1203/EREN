# EREN Epic 1 — Infrastructure Platform
*Version 1.0 - 2026-07-16*

---

## Purpose

Epic 1 builds the **technical platform** that all future EPICs run on. It establishes PostgreSQL, Redis, RabbitMQ, CI/CD pipelines, observability, and the core architectural patterns (Repository, Unit of Work, Outbox) that enforce consistency and reliability across the entire system.

Epic 1 must be **completed and stable** before any domain EPIC (2-10) can begin implementation.

---

## Epic Dependencies

```
Epic 0 ────────────────────────────────────────────→ Epic 1
  │                                                              │
  ├── Architecture Blueprint ──────────────────→ Full stack definition  │
  ├── Multi-Tenancy Strategy ────────────────→ Shared DB + RLS     │
  ├── Event Architecture ──────────────────────→ Outbox + RabbitMQ    │
  ├── Failure Model ────────────────────────────→ Health + circuit brk │
  ├── Consistency Model ────────────────────────→ PostgreSQL source     │
  └── Non-Functional Requirements ──────────────→ Latency targets     │

Epic 1 ────────────────────────────────────────────→ Epic 2
  │                                                              │
  ├── PostgreSQL + Alembic ────────────────────→ Domain data storage   │
  ├── Repository + Unit of Work ─────────────────→ Domain models        │
  ├── Outbox Pattern ────────────────────────────→ Event publishing     │
  ├── RabbitMQ ─────────────────────────────────→ Async messaging     │
  └── RLS ──────────────────────────────────────→ Multi-tenant safety  │

Epic 1 ────────────────────────────────────────────→ Epic 3
  │                                                              │
  └── All infrastructure layers ──────────────────→ Hospital domain    │

Epic 1 ────────────────────────────────────────────→ Epic 4
  │                                                              │
  └── FastAPI + observability ───────────────────→ AI Core platform   │
```

---

## Relationship to Epic 0

Epic 1 implements the infrastructure decisions documented in Epic 0. Read these **in parallel** with Epic 1:

| Epic 0 Document | What Epic 1 Implements |
|----------------|-----------------------|
| `EREN_ARCHITECTURE_BLUEPRINT.md` | Full stack definition |
| `EREN_MULTITENANCY_STRATEGY.md` | Shared DB + tenant_id + RLS |
| `EREN_FAILURE_MODEL.md` | Health checks, circuit breaker, retry |
| `EREN_EVENT_ARCHITECTURE.md` | Outbox pattern, event bus, DLQ |
| `EREN_ARCHITECTURAL_GUARDRAILS.md` | Repository pattern, no raw SQL |
| `EREN_NONFUNCTIONAL_REQUIREMENTS.md` | Latency targets, throughput |
| `EREN_CONSISTENCY_MODEL.md` | PostgreSQL source of truth |

---

## Document Index

| Document | Purpose | Status |
|---------|---------|--------|
| [README.md](./README.md) | This index | READY |
| [EREN_INFRASTRUCTURE_SETUP.md](./EREN_INFRASTRUCTURE_SETUP.md) | Local dev environment | READY |
| [EREN_DEPLOYMENT.md](./EREN_DEPLOYMENT.md) | Docker, K8s, GitOps | READY |
| [EREN_TESTING_GUIDE.md](./EREN_TESTING_GUIDE.md) | Testing strategy | READY |

---

## Architecture

Epic 1 delivers a **FastAPI monolithic API** that grows into microservices in EPIC 6+.

```
docs/adr/epic1/
├── ADR-0100.md  FastAPI as API Framework
├── ADR-0101.md  SQLAlchemy 2.0 ORM
├── ADR-0102.md  Alembic for Migrations
├── ADR-0103.md  Repository Pattern
├── ADR-0104.md  Unit of Work Pattern
├── ADR-0105.md  Outbox Pattern
├── ADR-0106.md  Redis Cache Strategy
├── ADR-0107.md  RabbitMQ Messaging
├── ADR-0108.md  OpenTelemetry Observability
├── ADR-0109.md  Structured Logging
└── ADR-0110.md  Health Check Strategy
```

---

## Stack Summary

```
apps/api/
├── app/
│   ├── config/          settings.py (pydantic-settings)
│   ├── core/           database.py (async SQLAlchemy 2.0)
│   ├── infrastructure/
│   │   ├── messaging/   rabbitmq.py + outbox.py + cache.py
│   │   ├── repositories/  device, incident, knowledge, recommendation
│   │   ├── models/     SQLAlchemy ORM models
│   │   ├── observability/  logging.py + tracing.py
│   │   ├── unit_of_work.py
│   │   └── vault/     HashiCorp Vault client
│   ├── middleware/     auth, audit, request_context
│   ├── routers/       health, auth, patients, diagnosis, devices, work_orders
│   └── main.py         FastAPI app factory
├── migrations/        6 Alembic migrations (001-006)
├── scripts/          migrate.py
└── tests/            17 unit + 3 integration tests
```

---

## Infrastructure Components

### Core Stack

| Component | Version | Purpose |
|----------|---------|---------|
| FastAPI | 0.115+ | HTTP API framework |
| SQLAlchemy | 2.0+ | ORM (async) |
| PostgreSQL | 16+ | Primary database |
| Redis | 7+ | Caching + sessions |
| RabbitMQ | 3.13+ | Async messaging |
| aio-pika | 9.4+ | Async RabbitMQ client |

### Observability

| Component | Version | Purpose |
|----------|---------|---------|
| OpenTelemetry | 1.24+ | Distributed tracing |
| Prometheus/Grafana | - | Metrics + dashboards |
| python-json-logger | 2.0+ | Structured JSON logs |
| Jaeger | 1.57 | Trace visualization |

### Infrastructure as Code

| Component | Purpose |
|----------|---------|
| `docker-compose.yml` | Local development |
| `infra/k8s/` | Kubernetes manifests |
| `infra/helm/` | Helm chart |
| `.github/workflows/ci.yml` | CI/CD pipeline |

---

## Epic 1 Complete — Ready for Epic 2

**Epic 1 Status:** COMPLETE ✅

**EPIC Roadmap Status:**
- EPIC 0 (Architecture) — COMPLETE ✅
- EPIC 0-Infra (Infrastructure Design) — COMPLETE ✅
- EPIC 1 (Infrastructure Platform) — COMPLETE ✅ (merged)
- **EPIC 2 (Core Domain) — IN PROGRESS 🚧**

| Component | Implementation |
|-----------|----------------|
| PostgreSQL | ✅ asyncpg, connection pooling |
| Alembic | ✅ 6 migrations, RLS support |
| SQLAlchemy | ✅ 5 models, async |
| Docker | ✅ Dockerfile + docker-compose |
| Redis | ✅ cache aside, TTL |
| RabbitMQ | ✅ topic exchange, aio-pika |
| Vault | ✅ client, env fallback |
| CI/CD | ✅ 4 jobs (lint + typecheck + test + build) |
| OpenTelemetry | ✅ FastAPI + SQLAlchemy instrumentation |
| Logging | ✅ structured JSON, correlation IDs |
| Health Checks | ✅ /health + /health/live + /health/ready + /health/full |
| Repository Pattern | ✅ 5 implementations |
| Unit of Work | ✅ async context manager |
| Outbox Pattern | ✅ TransactionalOutbox + OutboxWorker |
| Settings | ✅ pydantic-settings, env vars |

**Next:** Epic 2 - Core Business Domain
