# EREN — Architecture Overview

> High-level map of EREN's architecture as it exists **today**. For the deeper
> component design see [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md); for the cognitive
> core see [CORE_SPECIFICATION.md](./CORE_SPECIFICATION.md); for where we're going
> see [MASTER_ROADMAP.md](./MASTER_ROADMAP.md).

**Status:** the repository is in the **architecture-scaffolding** phase. The
monorepo, the backend skeleton, the cognitive-core engine skeletons and the
contracts layer exist; **no business logic, AI, or agents are implemented yet.**

---

## 1. What EREN is

EREN is a **Cognitive Operating System (COS)** specialized in Clinical
Engineering — not a chatbot and not a single application. It orchestrates
specialized cognitive engines over institutional knowledge to amplify the work of
biomedical engineers. The authoritative product definition lives in
[VISION.md](./VISION.md) and [ADR-0001](./docs/adr/ADR-0001-cognitive-operating-system.md).

## 2. Guiding principles

1. **Interface-agnostic cognition.** All intelligence lives in `core/`; delivery
   surfaces (`apps/*`) are thin.
2. **Inward dependency rule.** `apps/*` → `packages/*`/`core/*`; `core/*` never
   depends on `apps/*`; apps never depend on each other.
3. **Contracts first.** Engines depend on the abstractions in
   [`core/contracts`](./core/contracts), not on each other's concrete classes
   (Dependency Inversion).
4. **Explainability is mandatory.** Every cognitive decision must be auditable.
5. **Built to last.** Designed to scale to thousands of hospitals without major
   rewrites (see [MASTER_ROADMAP.md](./MASTER_ROADMAP.md)).

## 3. Layered view

```
┌──────────────────────────────────────────────────────────────┐
│  Delivery surfaces — apps/                                    │
│  web (Next.js)   ·   api (FastAPI)   ·   desktop (placeholder)│
└──────────────────────────────────────────────────────────────┘
                              ↓ depends on
┌──────────────────────────────────────────────────────────────┐
│  Cognitive core — core/                                       │
│  orchestrator · planner · reasoning · memory · knowledge      │
│  diagnostic · workflow · tools                                │
│  (+ core/contracts · core/context)                            │
└──────────────────────────────────────────────────────────────┘
                              ↓ depends on
┌──────────────────────────────────────────────────────────────┐
│  Shared libraries — packages/                                 │
│  shared · sdk · prompts · schemas                             │
└──────────────────────────────────────────────────────────────┘
                              ↓ runs on
┌──────────────────────────────────────────────────────────────┐
│  Infrastructure — infrastructure/  (database, IaC, ops)       │
└──────────────────────────────────────────────────────────────┘
```

## 4. Monorepo layout

```
eren/
├── apps/                # Deployable delivery surfaces
│   ├── web/             # Next.js web interface (@eren/web)
│   ├── api/             # FastAPI HTTP gateway (clean architecture)
│   └── desktop/         # Native desktop client (placeholder)
├── core/                # Cognitive core (interface-agnostic engines)
│   ├── contracts/       # Common interfaces every engine implements
│   ├── context/         # CognitiveContext: object shared across engines
│   ├── orchestrator/    # Coordinates engines & the cognitive request lifecycle
│   ├── planner/         # Decomposes goals into ordered plans
│   ├── reasoning/       # Explainable reasoning over evidence
│   ├── memory/          # Short- & long-term institutional memory
│   ├── knowledge/       # Structures & serves institutional knowledge
│   ├── diagnostic/      # Clinical-engineering fault analysis
│   ├── workflow/        # Long-running multi-step processes
│   └── tools/           # Registry/adapters for controlled capabilities
├── packages/            # Shared libraries (@eren/*)
│   ├── shared/          # Cross-cutting types/utilities/constants
│   ├── sdk/             # Typed client SDK
│   ├── prompts/         # Versioned prompt library
│   └── schemas/         # Shared data contracts / validation
├── infrastructure/      # IaC, CI/CD, database scripts, operations
│   └── database/        # SQL & diagnostic scripts
├── docs/                # Documentation (ADRs, architecture, domain, roadmap…)
└── tests/               # Cross-workspace (integration / e2e) tests
```

## 5. Technology at a glance

| Area | Choice |
| --- | --- |
| Web | Next.js (App Router, React 19), TypeScript, Tailwind CSS |
| API | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 (async), Alembic |
| Tooling (JS) | npm workspaces, ESLint |
| Tooling (Py) | uv, Ruff, Pytest |
| Data | Supabase (PostgreSQL); Qdrant vector DB (planned) |
| Auth | Supabase Auth (multi-hospital) |

See [docs/TECH_STACK_ANALYSIS.md](./docs/TECH_STACK_ANALYSIS.md) for rationale and
[SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) for how the pieces fit together.

## 6. Where things are documented

- **Decisions:** [docs/adr/](./docs/adr/) — Architecture Decision Records.
- **Cognitive core detail:** [CORE_SPECIFICATION.md](./CORE_SPECIFICATION.md).
- **Component/runtime design:** [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md).
- **Plan & milestones:** [MASTER_ROADMAP.md](./MASTER_ROADMAP.md).
- **Principles & vision:** [VISION.md](./VISION.md), [EREN_MANIFESTO.md](./EREN_MANIFESTO.md), [TECH_BIBLE.md](./TECH_BIBLE.md).

---

**Last updated:** 2026-07-13 · Aligned with the current monorepo, backend
skeleton, cognitive-core engines and contracts layer.
