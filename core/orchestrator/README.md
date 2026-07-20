# core/orchestrator — Orchestrator engine

> **Status:** scaffolding only. Classes, interfaces, models, diagrams and docs —
> **no logic, AI, or agents.** Method bodies raise `NotImplementedError`.

## Responsibility

The **heart of EREN** — the central nervous system of its cognition. The
orchestrator owns the end-to-end lifecycle of a cognitive request and does
**only** these things:

1. **Receive a context** — accept a `CognitiveContext` (request + tenant +
   correlation + metadata).
2. **Execute a plan** — walk the ordered steps of the planner's `Plan`.
3. **Invoke engines** — delegate each step to the responsible cognitive engine
   (reasoning, knowledge, memory, diagnostic, workflow, tools, …).
4. **Merge responses** — fuse the per-engine `EngineResponse`s.
5. **Return a result** — assemble an explainable `OrchestrationResult`.

It is the **only** engine that legitimately knows about the others; every other
engine stays independent and is composed *by* the orchestrator. It **does not**
plan, reason, or implement domain logic — it delegates. It knows nothing about
UI/transport (`apps/*`).

## Request lifecycle

```mermaid
flowchart LR
    CTX([CognitiveContext]) --> RCV["orchestrate()"]
    RCV --> EXE["execute_plan()"]
    EXE --> INV["invoke_engine() ×N"]
    INV --> MRG["merge_responses()"]
    MRG --> RES([OrchestrationResult])
```

## Coordination (composition, not inheritance)

```mermaid
sequenceDiagram
    participant Caller as apps/* (via SDK)
    participant O as OrchestratorEngine
    participant P as Planner
    participant E as Cognitive engines

    Caller->>O: orchestrate(context)
    O->>P: create_plan(intention)
    P-->>O: Plan (ordered steps)
    loop each step
        O->>E: invoke_engine(engine_id, context)
        E-->>O: EngineResponse
    end
    O->>O: merge_responses(context, responses)
    O-->>Caller: OrchestrationResult
```

## Data model

```mermaid
classDiagram
    class CognitiveContext {
        +str request
        +str tenant_id
        +str correlation_id
        +Mapping metadata
    }
    class EngineResponse {
        +str engine
        +object payload
        +float confidence
    }
    class ExecutionState {
        +CognitiveContext context
        +EngineResponse[] responses
    }
    class OrchestrationResult {
        +CognitiveContext context
        +EngineResponse[] responses
        +object output
    }
    ExecutionState --> CognitiveContext
    ExecutionState "1" --> "*" EngineResponse
    OrchestrationResult --> CognitiveContext
    OrchestrationResult "1" --> "*" EngineResponse
```

## Engine registry (Dependency Inversion)

The orchestrator receives its engines as a registry and depends only on the
`core.contracts.CognitiveEngine` abstraction — never on concrete engine classes:

```python
type EngineRegistry = Mapping[str, CognitiveEngine]

orchestrator = OrchestratorEngine(engines=registry)  # engines injected in
```

## Public API (scaffolding)

| Symbol | Kind | Purpose |
| --- | --- | --- |
| `OrchestratorEngine` | class | Runs the 5-stage request lifecycle (stubbed). |
| `OrchestratorPort` | `Protocol` | Contract callers depend on. |
| `EngineRegistry` | type alias | `Mapping[str, CognitiveEngine]` injected registry. |
| `CognitiveContext` | dataclass | Request input shape. |
| `EngineResponse` | dataclass | One engine's contribution. |
| `ExecutionState` | dataclass | Intermediate accumulated state. |
| `OrchestrationResult` | dataclass | Final explainable output. |
| `OrchestratorError` (+ subclasses) | exceptions | One base + one per lifecycle stage. |

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `OrchestratorEngine` — the 5 lifecycle stages as stubbed methods. |
| `interfaces.py` | `OrchestratorPort` + `EngineRegistry` type. |
| `models.py` | `CognitiveContext`, `EngineResponse`, `ExecutionState`, `OrchestrationResult`. |
| `exceptions.py` | `OrchestratorError` and per-stage subclasses. |

## Boundaries
- Domain-agnostic cognitive coordination — no UI/app/transport code.
- May depend on `core/contracts`, other `core/*` engines and `packages/*`;
  never on `apps/*`.
