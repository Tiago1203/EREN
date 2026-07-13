# core/contracts — Contracts layer

> **Status:** interfaces only. No logic, AI, or agents. Targets Python 3.12+.

The single source of truth for the **abstractions** every EREN cognitive engine
implements. Consumers (the orchestrator, `apps/*`) depend on these contracts, not
on concrete engine classes — so engines are swappable and testable in isolation.

## Interfaces

| Contract | Module | Responsibility |
| --- | --- | --- |
| `CognitiveEngine` | `base.py` | Common capability shared by **all** engines (`name`, `describe`). |
| `SupportsLifecycle` | `base.py` | Optional `startup`/`shutdown` for engines that own resources. |
| `Tool` | `tool.py` | A controlled, invokable leaf capability (not an engine). |
| `Planner` | `planner.py` | Decompose a goal into an ordered plan; re-plan. |
| `Memory` | `memory.py` | Remember / recall / forget contextual & institutional memory. |
| `Knowledge` | `knowledge.py` | Ingest and search curated institutional knowledge. |
| `Workflow` | `workflow.py` | Start / advance / inspect stateful multi-step processes. |
| `Diagnostic` | `diagnostic.py` | Analyze symptoms and produce justified hypotheses. |
| `Reasoning` | `reasoning.py` | Draw explainable conclusions from evidence. |

Every specialized engine contract **extends `CognitiveEngine`** (a `Planner`
*is-a* `CognitiveEngine`), so anything that needs "some engine" accepts the base
type, while code needing planning depends on the narrower `Planner`.

## How the SOLID principles are applied

- **S — Single Responsibility:** one interface per capability, one method group per concern.
- **O — Open/Closed:** interfaces are generic over their domain types
  (e.g. `Planner[Goal, Plan]`), so new domains extend usage without changing the contract.
- **L — Liskov Substitution:** specialized contracts subtype `CognitiveEngine`;
  any concrete engine is usable wherever its interface is expected.
- **I — Interface Segregation:** small, focused protocols. `Tool` is deliberately
  **not** a `CognitiveEngine`; lifecycle is split into `SupportsLifecycle` so
  stateless engines aren't forced to implement it.
- **D — Dependency Inversion:** high-level code (orchestrator) and low-level code
  (concrete engines) both depend on these abstractions.

## Modern typing

- `typing.Protocol` + `@runtime_checkable` — structural typing, no forced inheritance.
- **PEP 695** type parameters, e.g. `class Planner[Goal, Plan](CognitiveEngine, Protocol)`.
- `from __future__ import annotations` and `collections.abc.Sequence` throughout.

## Usage

```python
from core.contracts import CognitiveEngine, Planner

def register(engine: CognitiveEngine) -> None:
    ...  # depends only on the abstraction
```

Method bodies here are `...` by design — this package defines *contracts*, and
the engines under `core/<engine>/` provide the implementations.
