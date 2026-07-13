# core/diagnostic — Diagnostic

Clinical-engineering diagnostic engine: structures fault analysis and troubleshooting workflows over equipment and cases.

> **Status:** placeholder. This module is part of the EREN architecture
> scaffolding. No business logic, AI, or agents are implemented here yet.

## Purpose

Clinical-engineering diagnostic engine: structures fault analysis and troubleshooting workflows over equipment and cases.

## Boundaries

- Contains **domain-agnostic cognitive capability**, not app or UI code.
- Consumed by `apps/*` (web, api, desktop) and other `core/*` engines.
- Must not depend on any specific delivery interface.
