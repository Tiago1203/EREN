# core/tools — Tools engine

> **Status:** scaffolding only. Empty classes, no logic, AI, or agents yet.

## Responsibility

The **capability registry and adapter layer**. It provides a controlled catalog
of the external tools/integrations the cognitive engines are allowed to invoke
(databases, external services, calculators, retrieval backends, etc.), exposing
them behind a uniform, governable interface.

Its job is *registration, discovery and safe invocation* of capabilities — so
the orchestrator and other engines can use external actions without depending on
vendor-specific details. It contains no tool business logic itself; each concrete
tool is an adapter plugged into this registry.

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `ToolsEngine` — register, discover and invoke tools/adapters. |
| `interfaces.py` | `ToolsPort` — contract for registering and calling tools. |
| `exceptions.py` | `ToolsError` — base error for tool registry/invocation failures. |
| `models.py` | Data structures for tool descriptors, inputs and outputs. |

## Boundaries
- Capability brokering only — no UI; concrete integrations live as adapters.
- May depend on `packages/*`; never on `apps/*`.
