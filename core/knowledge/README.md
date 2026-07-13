# core/knowledge — Knowledge

Structures, indexes and serves institutional clinical-engineering knowledge to the other engines.

> **Status:** placeholder. This module is part of the EREN architecture
> scaffolding. No business logic, AI, or agents are implemented here yet.

## Purpose

Structures, indexes and serves institutional clinical-engineering knowledge to the other engines.

## Boundaries

- Contains **domain-agnostic cognitive capability**, not app or UI code.
- Consumed by `apps/*` (web, api, desktop) and other `core/*` engines.
- Must not depend on any specific delivery interface.
