# core/workflow — Workflow

Defines and executes long-running, multi-step operational processes and their state transitions.

> **Status:** placeholder. This module is part of the EREN architecture
> scaffolding. No business logic, AI, or agents are implemented here yet.

## Purpose

Defines and executes long-running, multi-step operational processes and their state transitions.

## Boundaries

- Contains **domain-agnostic cognitive capability**, not app or UI code.
- Consumed by `apps/*` (web, api, desktop) and other `core/*` engines.
- Must not depend on any specific delivery interface.
