# core/planner — Planner engine

> **Status:** scaffolding only. Empty classes, no logic, AI, or agents yet.

## Responsibility

Turns a **high-level goal into an ordered, executable plan**. Given an
objective and context, the planner decomposes it into discrete steps, expresses
their dependencies/ordering, and produces a plan the orchestrator can execute.
It is also responsible for **re-planning** when a step fails or new information
arrives.

The planner decides *what should happen and in what order* — it does not execute
the steps (that is the orchestrator/workflow) nor perform the reasoning within a
step (that is the reasoning engine).

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `PlannerEngine` — builds and revises plans from goals. |
| `interfaces.py` | `PlannerPort` — contract to request a plan / re-plan. |
| `exceptions.py` | `PlannerError` — base error for planning failures. |
| `models.py` | Data structures for goals, steps and plans. |

## Boundaries
- Pure planning capability — no delivery/UI code.
- May depend on `packages/*`; never on `apps/*`.
