# core/reasoning — Reasoning engine

> **Status:** scaffolding only. Empty classes, no logic, AI, or agents yet.

## Responsibility

Applies **explainable reasoning strategies over evidence** to reach conclusions.
Given a question and a set of evidence (from memory, knowledge, diagnostic, etc.),
the reasoning engine produces an answer/decision **together with an auditable
justification** — the chain of evidence and inference that led to it.

Explainability is a first-class requirement in EREN: this engine must always be
able to expose *why* a conclusion was reached, not just the conclusion.

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `ReasoningEngine` — evidence-based, explainable reasoning. |
| `interfaces.py` | `ReasoningPort` — contract to submit a question + evidence and get a justified conclusion. |
| `exceptions.py` | `ReasoningError` — base error for reasoning failures. |
| `models.py` | Data structures for evidence, conclusions and justifications. |

## Boundaries
- Reasoning capability only — no domain data ownership, no UI.
- May depend on `packages/*`; never on `apps/*`.
