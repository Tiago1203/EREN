# core/

The **cognitive core** of EREN — the domain and cognition layer that makes
EREN a Cognitive Operating System rather than an application.

Each subdirectory is a specialized engine with a single responsibility. They
are interface-agnostic: they know nothing about web, API, or desktop delivery.
`apps/*` compose these engines; `core/*` never depends on `apps/*`.

> **Status:** placeholder scaffolding. No business logic, AI, or agents are
> implemented yet.

## Engines

| Engine | Responsibility |
| --- | --- |
| [`orchestrator/`](./orchestrator) | Coordinates engines and manages the cognitive request lifecycle. |
| [`planner/`](./planner) | Decomposes goals into executable, ordered steps. |
| [`reasoning/`](./reasoning) | Explainable reasoning strategies over evidence. |
| [`memory/`](./memory) | Short- and long-term institutional memory. |
| [`diagnostic/`](./diagnostic) | Clinical-engineering fault analysis and troubleshooting. |
| [`workflow/`](./workflow) | Long-running multi-step operational processes. |
| [`knowledge/`](./knowledge) | Structures and serves institutional knowledge. |
| [`tools/`](./tools) | Registry/adapters for controlled capabilities and integrations. |

## Shared cognitive context

| Package | Responsibility |
| --- | --- |
| [`context/`](./context) | `CognitiveContext` — the Pydantic v2 object that travels through every engine during one interaction. |

## Internal event system

| Package | Responsibility |
| --- | --- |
| [`events/`](./events) | `Event`/`EventType`, `EventPublisher`/`EventSubscriber` and the `EventBus` — decoupled pub/sub between engines. |

## Engine registry

| Package | Responsibility |
| --- | --- |
| [`registry/`](./registry) | `EngineRegistry` — dynamic, dependency-injected registration and lookup of engines by name (no conditional dispatch). |

## Contracts

| Package | Responsibility |
| --- | --- |
| [`contracts/`](./contracts) | SOLID `typing.Protocol` interfaces every engine implements. |

## Dependency rules

- `core/*` may depend on `packages/*` (shared contracts/utilities).
- `core/*` must **not** depend on `apps/*`.
- Cross-engine calls go **through** the orchestrator where possible.
