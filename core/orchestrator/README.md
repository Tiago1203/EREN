# core/orchestrator — Orchestrator

Coordinates the cognitive engines: routes work between planner, reasoning, memory and tools, and manages the lifecycle of a cognitive request end to end.

> **Status:** placeholder. This module is part of the EREN architecture
> scaffolding. No business logic, AI, or agents are implemented here yet.

## Purpose

Coordinates the cognitive engines: routes work between planner, reasoning, memory and tools, and manages the lifecycle of a cognitive request end to end.

## Boundaries

- Contains **domain-agnostic cognitive capability**, not app or UI code.
- Consumed by `apps/*` (web, api, desktop) and other `core/*` engines.
- Must not depend on any specific delivery interface.
