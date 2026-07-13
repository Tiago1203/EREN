# core/memory — Memory

Manages short- and long-term institutional memory: capture, retrieval and consolidation of knowledge and context.

> **Status:** placeholder. This module is part of the EREN architecture
> scaffolding. No business logic, AI, or agents are implemented here yet.

## Purpose

Manages short- and long-term institutional memory: capture, retrieval and consolidation of knowledge and context.

## Boundaries

- Contains **domain-agnostic cognitive capability**, not app or UI code.
- Consumed by `apps/*` (web, api, desktop) and other `core/*` engines.
- Must not depend on any specific delivery interface.
