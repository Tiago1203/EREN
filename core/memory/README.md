# core/memory — Memory engine

> **Status:** scaffolding only. Empty classes, no logic, AI, or agents yet.

## Responsibility

Manages EREN's **institutional and conversational memory**. It stores, retrieves
and consolidates context across two horizons:

- **Short-term memory** — the working context of an ongoing interaction
  (the Memory Base / conversation history).
- **Long-term memory** — durable institutional context that persists across
  interactions and users.

The memory engine is responsible for *remembering and recalling* relevant
context on demand; it does not interpret it (reasoning) or structure external
documents (knowledge).

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `MemoryEngine` — store/retrieve/consolidate context. |
| `interfaces.py` | `MemoryPort` — contract to write and query memory. |
| `exceptions.py` | `MemoryError` — base error for memory failures. |
| `models.py` | Data structures for memory records and queries. |

## Boundaries
- Memory capability only — persistence details are injected, not hard-coded to a vendor.
- May depend on `packages/*`; never on `apps/*`.
