# core/tools — Tools

Registry and adapters for the capabilities (integrations, actions) the engines can invoke in a controlled way.

> **Status:** placeholder. This module is part of the EREN architecture
> scaffolding. No business logic, AI, or agents are implemented here yet.

## Purpose

Registry and adapters for the capabilities (integrations, actions) the engines can invoke in a controlled way.

## Boundaries

- Contains **domain-agnostic cognitive capability**, not app or UI code.
- Consumed by `apps/*` (web, api, desktop) and other `core/*` engines.
- Must not depend on any specific delivery interface.
