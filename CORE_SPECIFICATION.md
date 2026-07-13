# EREN CORE — Specification

> Authoritative specification of the EREN cognitive core (`core/`) as it exists
> today. See [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) for context
> and [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) for the surrounding system.

**Status:** scaffolding phase — engine classes and interfaces exist as **empty,
documented skeletons**. **No business logic, AI, or agents are implemented yet.**

---

## 1. Overview

`core/` is EREN's interface-agnostic cognition layer. It is composed of eight
specialized **engines** and one **contracts layer** that defines the interfaces
every engine implements. Delivery surfaces (`apps/*`) compose these engines;
`core/*` never depends on `apps/*`.

Each engine directory contains:

```
core/<engine>/
├── README.md        # the engine's exact responsibility + boundaries
├── __init__.py      # re-exports <Prefix>Engine, <Prefix>Error, <Prefix>Port
├── engine.py        # class <Prefix>Engine  (empty skeleton)
├── interfaces.py    # class <Prefix>Port(Protocol)  (engine-local port)
├── exceptions.py    # class <Prefix>Error(Exception)
└── models.py        # domain models (defined as the engine grows)
```

## 2. The contracts layer (`core/contracts`)

The single source of truth for the abstractions engines implement. Pure
`typing.Protocol` interfaces using modern Python (PEP 695 generics, targets
3.12+). Consumers depend on these, not on concrete engines (Dependency
Inversion). See [`core/contracts/README.md`](./core/contracts/README.md).

| Contract | Shape | Purpose |
| --- | --- | --- |
| `CognitiveEngine` | `name`, `describe()` | Capability shared by **all** engines. |
| `SupportsLifecycle` | `startup()`, `shutdown()` | Optional resource lifecycle (segregated). |
| `Tool[TInput, TOutput]` | `name`, `description`, `invoke()` | A leaf capability — **not** an engine. |
| `Planner[Goal, Plan]` | `plan()`, `replan()` | Goal → ordered plan. |
| `Memory[Record, Query]` | `remember()`, `recall()`, `forget()` | Store/recall context. |
| `Knowledge[Item, Query]` | `ingest()`, `search()` | Index/serve knowledge. |
| `Workflow[Definition, Instance, State]` | `start()`, `advance()`, `state_of()` | Stateful processes. |
| `Diagnostic[Symptoms, Diagnosis]` | `diagnose()` | Fault analysis. |
| `Reasoning[Question, Evidence, Conclusion]` | `reason()` | Explainable conclusions. |

Every specialized contract subtypes `CognitiveEngine` (Liskov Substitution);
`Tool` is intentionally separate (Interface Segregation). The SOLID rationale is
documented in the contracts README.

## 3. The engines

The canonical EREN CORE consists of these eight engines.

### 3.1 Orchestrator
Central coordinator. Owns the end-to-end lifecycle of a cognitive request:
decides which engines to involve and in what order, moves data between them,
manages intermediate state, and assembles the final explainable result. The only
engine aware of the others; it delegates rather than implementing cognition.

### 3.2 Planner
Decomposes a high-level goal into an ordered, executable plan and re-plans when a
step fails or new information arrives. Decides *what and in what order*, not how a
step reasons. Implements `Planner[Goal, Plan]`.

### 3.3 Reasoning
Applies explainable reasoning strategies over evidence to reach conclusions
**with an auditable justification**. Explainability is a first-class requirement.
Implements `Reasoning[Question, Evidence, Conclusion]`.

### 3.4 Memory
Manages short-term (conversation/context) and long-term (institutional) memory:
store, recall, consolidate, forget. Remembers *what happened/was said*.
Implements `Memory[Record, Query]`.

### 3.5 Knowledge
Structures, indexes and serves curated institutional knowledge — Knowledge Base
(manuals), Case Base (resolved cases), Document Base (protocols/norms). Owns
*what the institution knows*. Implements `Knowledge[Item, Query]`.

### 3.6 Diagnostic
Clinical-engineering fault analysis: given equipment symptoms, produces ranked,
justified troubleshooting hypotheses, drawing on knowledge and past cases. EREN's
domain-specialized engine. Implements `Diagnostic[Symptoms, Diagnosis]`.

### 3.7 Workflow
Models and drives long-running, stateful, multi-step operational processes (e.g.
preventive maintenance) — states, transitions, and instance progress. Governs
durable processes, distinct from the planner's per-request sequencing. Implements
`Workflow[Definition, Instance, State]`.

### 3.8 Tools
Registry and adapter layer for controlled external capabilities the engines may
invoke, behind a uniform, governable interface. Concrete integrations are
adapters plugging into this registry. Implements the `Tool` contract per adapter.

## 4. Dependency rules

- `core/*` may depend on `core/contracts` and `packages/*`.
- `core/*` must **not** depend on `apps/*`.
- Cross-engine collaboration goes **through** the orchestrator where possible.
- Each engine's local `interfaces.py` port aligns with the shared contract of the
  same capability in `core/contracts`.

## 5. Explainability & safety (design constraints)

- Reasoning and diagnostic outputs must carry a justification / evidence trail.
- Tool invocation is mediated by the tools registry (controlled, governable).
- No engine bypasses the contracts to reach into another engine's internals.

## 6. Cross-cutting capabilities (planned)

Concerns previously modeled as separate engines — **learning**, **permission/
authorization**, and **audit** — are tracked as future capabilities or
cross-cutting infrastructure rather than part of the current canonical eight.
See [docs/core/eren-core-cognitive-engines.md](./docs/core/eren-core-cognitive-engines.md)
for the extended catalog and [MASTER_ROADMAP.md](./MASTER_ROADMAP.md) for timing.

## 7. Related decisions

- [ADR-0002](./docs/adr/ADR-0002-eren-core-architecture.md) — EREN CORE architecture.
- [ADR-0030](./docs/adr/) — cognitive engines strategy (index).
- Contracts SOLID rationale — [`core/contracts/README.md`](./core/contracts/README.md).

---

**Last updated:** 2026-07-13 · Reflects the eight core engines and the contracts
layer currently in the repository.
