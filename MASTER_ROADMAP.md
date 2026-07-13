# EREN — Master Roadmap

> The single, authoritative roadmap for EREN. It reconciles the product vision
> with the **current state of the repository** and the detailed
> [docs/roadmap/complete-roadmap.md](./docs/roadmap/complete-roadmap.md).

**Where we are today:** architecture-scaffolding phase. The monorepo, the FastAPI
backend skeleton, the eight cognitive-core engine skeletons and the contracts
layer exist. **No business logic, AI, or agents are implemented yet.**

---

## 1. Phases

| Phase | Versions | Theme |
| --- | --- | --- |
| Foundation | pre-v0.1.0 | Monorepo, backend skeleton, core engine + contracts scaffolding *(current)* |
| Validation | v0.1.0 – v0.2.0 | Prove the concept; build the core |
| Advancement | v0.3.0 – v1.0.0 | Advanced capabilities & production stability |
| Scale | v2.0.0 – v3.0.0 | Horizontal scale & advanced intelligence |
| Ecosystem | v4.0.0 – v5.0.0 | Open platform & clinical vision |

## 2. Foundation (current) — architecture scaffolding

Delivered in this phase (no product logic yet):

- **Monorepo** with `apps/`, `core/`, `packages/`, `infrastructure/`, `docs/`,
  `tests/` and per-folder READMEs; npm workspaces at the root.
- **apps/web** — existing Next.js app relocated to `apps/web` (`@eren/web`),
  behavior preserved.
- **apps/api** — FastAPI clean-architecture skeleton (Python 3.12, uv, Pydantic
  v2, SQLAlchemy 2 async, Alembic, Ruff, Pytest); only a `/api/v1/health`
  liveness endpoint.
- **core/** — eight engine skeletons (orchestrator, planner, reasoning, memory,
  knowledge, diagnostic, workflow, tools) as empty documented classes.
- **core/contracts/** — SOLID interface layer (`CognitiveEngine`, `Tool`,
  `Planner`, `Memory`, `Knowledge`, `Workflow`, `Diagnostic`, `Reasoning`).
- **Documentation** — this document set plus updated ADRs and README.

**Exit criteria → v0.1.0:** engines implement their contracts with real (initial)
logic; the orchestrator can run a minimal end-to-end cognitive request through the
API and web surfaces.

## 3. v0.1.0 — MVP (target Q3 2026)

- Multi-hospital authentication (Supabase Auth).
- Equipment inventory + maintenance orders (basic).
- Case Base + vector search over technical knowledge.
- Conversational entry point wired through `core/orchestrator`.
- Four knowledge bases online: Knowledge, Case, Memory, Document.
- First working engines: **orchestrator, knowledge, memory, reasoning, tools**.
- **Targets:** 2 pilot hospitals · 50+ users · 100+ cases.

## 4. v0.2.0 — Core (target Q4 2026)

- **planner** and **workflow** engines operational.
- Automatic document ingestion + knowledge validation.
- Granular permissions (cross-cutting authorization).
- Redis caching; richer observability; integration tests.
- **Targets:** 5 hospitals · 200+ users.

## 5. v0.3.0 — Advanced (target Q1 2027)

- **diagnostic** engine operational (fault hypotheses from symptoms/cases).
- Optional multi-hospital collaboration (anonymized case sharing).
- Basic HL7/DICOM integration; mobile web.
- **Targets:** 10 hospitals · 500+ users.

## 6. v1.0.0 — Production (target Q2 2027)

- 99.9% uptime, disaster recovery, full observability & alerting.
- Complete API (OpenAPI), admin/integration guides.
- Full CI/CD (GitHub Actions), automated tests & deploys, security scanning.
- **Targets:** 20+ hospitals · 1,000+ users.

## 7. v2.0.0 – v3.0.0 — Scale & Intelligence (2027–2028)

- Kubernetes; selective microservices; Qdrant sharding; PostgreSQL read replicas.
- **learning** capability (ML): failure prediction, anomaly detection,
  process optimization; advanced analytics; native mobile.
- **Targets:** 50 → 100+ hospitals.

## 8. v4.0.0 – v5.0.0 — Ecosystem & Vision (2028–2029)

- Public API, SDK and plugin marketplace; EMR/EHR (FHIR) interoperability;
  research platform.
- Global hospital network; clinical decision support.
- **Targets:** 200 → 500+ hospitals; 10,000+ long-term.

## 9. Engine delivery matrix

| Engine | First target |
| --- | --- |
| orchestrator | v0.1.0 |
| knowledge | v0.1.0 |
| memory | v0.1.0 |
| reasoning | v0.1.0 |
| tools | v0.1.0 |
| planner | v0.2.0 |
| workflow | v0.2.0 |
| diagnostic | v0.3.0 |
| learning *(cross-cutting/ML)* | v2.0.0+ |

## 10. Success metrics (summary)

| Metric | v0.1.0 | v1.0.0 | v3.0.0 | v5.0.0 |
| --- | --- | --- | --- | --- |
| Hospitals | 2 | 20 | 100 | 500 |
| Active users | 50 | 1,000 | 20,000 | 200,000 |
| Uptime | — | 99.9% | 99.99% | 99.999% |

Full per-version breakdown, milestones and technical metrics:
[docs/roadmap/complete-roadmap.md](./docs/roadmap/complete-roadmap.md).

---

**Last updated:** 2026-07-13 · Reconciled with the current repository state and
the eight-engine cognitive core.
