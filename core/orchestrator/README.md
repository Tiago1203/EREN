# core/orchestrator — Orchestrator engine

> **Status:** scaffolding only. Empty classes, no logic, AI, or agents yet.

## Responsibility

The **central nervous system** of EREN's cognition. The orchestrator owns the
end-to-end lifecycle of a cognitive request: it receives a goal/request, decides
**which engines to involve and in what order**, coordinates the flow of data
between them (planner → reasoning → memory → knowledge → diagnostic → tools →
workflow), manages intermediate state, and assembles the final, explainable
result.

It is the only engine that legitimately knows about the others; every other
engine stays independent and is composed *by* the orchestrator. It does **not**
implement planning, reasoning, or domain logic itself — it delegates.

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `OrchestratorEngine` — coordinates engines and request lifecycle. |
| `interfaces.py` | `OrchestratorPort` — contract callers (e.g. `apps/*`) use to run a cognitive request. |
| `exceptions.py` | `OrchestratorError` — base error for orchestration failures. |
| `models.py` | Data structures for requests, execution state and results. |

## Boundaries
- Domain-agnostic cognitive coordination — no UI/app/transport code.
- May depend on other `core/*` engines and `packages/*`; never on `apps/*`.
