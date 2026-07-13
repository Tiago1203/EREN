# core/workflow — Workflow engine

> **Status:** scaffolding only. Empty classes, no logic, AI, or agents yet.

## Responsibility

Models and drives **long-running, multi-step operational processes** — e.g. a
preventive-maintenance procedure or an incident-resolution workflow. It defines
the states of a process, the allowed transitions between them, and tracks the
progress of a running instance until completion.

Where the **planner** decides the abstract sequence of steps for a single
cognitive request, the **workflow** engine governs durable, stateful business
processes that may span time, users and interactions.

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `WorkflowEngine` — define and advance stateful processes. |
| `interfaces.py` | `WorkflowPort` — contract to start/advance/query a workflow. |
| `exceptions.py` | `WorkflowError` — base error for workflow failures. |
| `models.py` | Data structures for workflow definitions, states and instances. |

## Boundaries
- Process orchestration capability — no UI; persistence is injected.
- May depend on `packages/*`; never on `apps/*`.
