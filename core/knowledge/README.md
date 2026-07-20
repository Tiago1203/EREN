# core/knowledge — Knowledge engine

> **Status:** scaffolding only. Empty classes, no logic, AI, or agents yet.

## Responsibility

Structures, indexes and **serves institutional knowledge** — the curated,
authoritative content of the organization: technical manuals (Knowledge Base),
resolved historical cases (Case Base), and regulatory protocols/norms (Document
Base). Given a query, it returns the most relevant knowledge with provenance.

Unlike `memory` (which recalls *what happened / was said*), the knowledge engine
owns *what the institution knows* and makes it retrievable for reasoning and
diagnostics.

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `KnowledgeEngine` — index and retrieve institutional knowledge. |
| `interfaces.py` | `KnowledgePort` — contract to query/ingest knowledge. |
| `exceptions.py` | `KnowledgeError` — base error for knowledge failures. |
| `models.py` | Data structures for knowledge items, sources and query results. |

## Boundaries
- Knowledge capability only — no UI; storage/index backends are injected.
- May depend on `packages/*`; never on `apps/*`.
