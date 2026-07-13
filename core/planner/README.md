# core/planner — Planner

Decomposes goals into ordered, executable steps and decides which engines and tools to invoke to accomplish a task.

> **Status:** placeholder. This module is part of the EREN architecture
> scaffolding. No business logic, AI, or agents are implemented here yet.

## Purpose

Decomposes goals into ordered, executable steps and decides which engines and tools to invoke to accomplish a task.

## Boundaries

- Contains **domain-agnostic cognitive capability**, not app or UI code.
- Consumed by `apps/*` (web, api, desktop) and other `core/*` engines.
- Must not depend on any specific delivery interface.
