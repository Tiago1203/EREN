# core/diagnostic — Diagnostic engine

> **Status:** scaffolding only. Empty classes, no logic, AI, or agents yet.

## Responsibility

The **clinical-engineering fault-analysis** capability. Given the symptoms of a
malfunctioning biomedical device (error codes, observed behavior, equipment
metadata, history), the diagnostic engine analyzes the situation and proposes
**ranked troubleshooting hypotheses and next steps**, drawing on knowledge and
past cases and justifying each hypothesis.

This is EREN's domain-specialized engine: it encodes *how a biomedical engineer
diagnoses equipment failures* as an orchestrated capability.

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `DiagnosticEngine` — analyze faults, propose hypotheses. |
| `interfaces.py` | `DiagnosticPort` — contract to submit symptoms and get a diagnosis. |
| `exceptions.py` | `DiagnosticError` — base error for diagnostic failures. |
| `models.py` | Data structures for symptoms, hypotheses and recommendations. |

## Boundaries
- Diagnostic reasoning about equipment — no UI; relies on other engines for evidence.
- May depend on `packages/*`; never on `apps/*`.
