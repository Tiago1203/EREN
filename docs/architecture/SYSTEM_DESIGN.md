# EREN — System Design

> Component- and runtime-level design of EREN. Read
> [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) first for the big picture,
> and [CORE_SPECIFICATION.md](./CORE_SPECIFICATION.md) for the cognitive engines.

**Status:** scaffolding phase. This document describes the *intended* design that
the current skeleton is shaped for. Sections marked _(planned)_ are not
implemented yet.

---

## 1. Design goals

- **Separation of concerns:** delivery, cognition, shared contracts and
  infrastructure are distinct layers with a strict inward dependency rule.
- **Substitutability:** every engine and adapter sits behind an interface so it
  can be replaced or mocked (Dependency Inversion / testability).
- **Explainability & auditability:** the design carries correlation/context and
  justification through every call.
- **Horizontal scalability:** stateless delivery surfaces; state pushed to
  managed data stores.

## 2. Component model

### 2.1 Delivery surfaces (`apps/`)

| App | Package | Stack | Responsibility |
| --- | --- | --- | --- |
| `apps/web` | `@eren/web` | Next.js (App Router, React 19), Tailwind | Human-facing UI; auth via Supabase; renders conversational/visual surfaces. |
| `apps/api` | `eren-api` | FastAPI, Pydantic v2, SQLAlchemy 2 async | Programmatic gateway; transport/validation only, delegates cognition to `core/`. |
| `apps/desktop` | — | placeholder | Future native client. |

Apps are **thin**: they translate transport ↔ domain and call into `core/`. They
never contain cognitive logic.

### 2.2 Cognitive core (`core/`)

Eight engines plus a contracts layer. Each engine is interface-agnostic and
depends only on `core/contracts` and `packages/*`. Detailed responsibilities and
interfaces are in [CORE_SPECIFICATION.md](./CORE_SPECIFICATION.md).

### 2.3 Shared libraries (`packages/`)

- `@eren/shared` — cross-cutting types, utilities, constants.
- `@eren/sdk` — typed client for programmatic COS access.
- `@eren/prompts` — versioned prompt library.
- `@eren/schemas` — shared data contracts / validation.

### 2.4 Infrastructure (`infrastructure/`)

Database scripts (`infrastructure/database`), and — _(planned)_ — IaC, CI/CD and
operational tooling.

## 3. Backend design (`apps/api`)

Clean architecture; dependencies point inward: `routers → services → models`,
with `schemas` as the contract and `core`/`config` as infrastructure.

```
apps/api/app/
├── main.py        # create_app() factory: middleware, exception handlers, routers
├── config/        # pydantic-settings Settings (env prefix EREN_API_)
├── core/          # database (async engine/session), logging, exceptions
├── middleware/    # RequestContextMiddleware (X-Request-ID correlation)
├── routers/       # api_router aggregator, mounted under /api/v1
├── schemas/       # Pydantic v2 DTOs
├── services/      # use-case layer (placeholder)
└── models/        # SQLAlchemy 2 DeclarativeBase
```

Key properties already in place:

- **App factory** `create_app()` wires CORS, `RequestContextMiddleware`, exception
  handlers, and mounts `api_router` under `settings.api_v1_prefix` (`/api/v1`).
- **Correlation:** every response carries an `X-Request-ID` (generated or echoed).
- **Async DB layer** is lazily initialized so importing the app never opens a
  connection; `Settings.database_url_sync` adapts the URL for Alembic.
- **Only endpoint today:** `GET /api/v1/health` (liveness probe).

See the backend decisions (clean architecture, API versioning) in the
[ADR index](./docs/adr/README.md) — planned as ADR-0011 and ADR-0015.

## 4. Frontend design (`apps/web`)

- **App Router** with route groups for auth and dashboard surfaces.
- **Middleware** guards protected routes and redirects unauthenticated users to
  `/login`; authenticated users hitting `/login` go to `/dashboard`.
- **Supabase** (`@supabase/ssr`, `@supabase/supabase-js`) for auth/session.
- Module aliasing via `@/*`; styling with Tailwind CSS 4 through
  `@tailwindcss/postcss`.

## 5. Request flow _(planned target)_

```
Client → apps/{web,api}           # transport, auth, validation
        → core/orchestrator       # decides which engines to run, in what order
          → planner               # decompose goal into steps
          → reasoning             # justified conclusions over evidence
          → memory / knowledge    # recall context / retrieve knowledge
          → diagnostic            # equipment fault hypotheses
          → tools                 # controlled external capabilities
          → workflow              # drive durable multi-step processes
        ← orchestrator            # assembles explainable result
```

The orchestrator is the only component aware of the other engines; everything
else stays independent behind `core/contracts`.

## 6. Data design

| Store | Role | Status |
| --- | --- | --- |
| Supabase (PostgreSQL) | Relational data, auth, RLS per hospital | In use (web) |
| SQLAlchemy 2 + Alembic | ORM & migrations for `apps/api` | Skeleton (SQLite default) |
| Qdrant | Vector search over knowledge/cases | Planned |
| Redis | Hot cache / queues | Planned |

Knowledge is organized as four bases: **Knowledge Base** (manuals), **Case Base**
(resolved cases), **Memory Base** (conversation/context) and **Document Base**
(protocols/norms). See [docs/knowledge/](./docs/knowledge/) and
[docs/data/](./docs/data/).

## 7. Cross-cutting concerns

- **Correlation/observability:** `X-Request-ID` today; structured logging,
  tracing and metrics _(planned)_.
- **Security:** Supabase Auth, Row Level Security per hospital, secrets never
  committed. Encryption and compliance (HIPAA/GDPR) tracked in the security ADRs.
- **Explainability:** reasoning outputs must carry justification; enforced by the
  `Reasoning` contract.

## 8. Environments & tooling

- **JS:** npm workspaces — `npm run dev|build|lint` from the root target `@eren/web`.
- **Python:** uv — `cd apps/api && uv run uvicorn app.main:app --reload`;
  `uv run ruff check .`; `uv run pytest`.

---

**Last updated:** 2026-07-13 · Consistent with the current monorepo, backend
skeleton, cognitive-core engines and contracts layer.
