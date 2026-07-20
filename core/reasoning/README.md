# core/reasoning — Reasoning engine

> **Status:** IMPLEMENTED ✅

## Responsibility

Applies **explainable reasoning strategies over evidence** to reach conclusions.
Given a question and a set of evidence (from memory, knowledge, diagnostic, etc.),
the reasoning engine produces an answer/decision **together with an auditable
justification** — the chain of evidence and inference that led to it.

Explainability is a first-class requirement in EREN: this engine must always be
able to expose *why* a conclusion was reached, not just the conclusion.

## Implemented Features

### Reasoning Strategies
- **Deductive**: General → Specific reasoning
- **Inductive**: Specific → General generalization
- **Abductive**: Observation → Best explanation
- **Analogical**: Similarity-based reasoning
- **Causal**: Cause → Effect tracing

### Evidence Management
- Evidence storage and retrieval
- Source tracking (document, sensor, user, llm)
- Confidence scoring
- Metadata support

### Confidence Scoring
- Automatic confidence level determination
- Five levels: Very High, High, Medium, Low, Very Low
- Based on evidence quality and consistency

### Explainability
- Human-readable explanations
- Full reasoning chain trace
- Alternative conclusions
- Evidence attribution

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | `ReasoningEngine` — full implementation with 5 strategies |
| `interfaces.py` | `ReasoningPort` — contract to submit a question + evidence |
| `exceptions.py` | `ReasoningError` — base error for reasoning failures |
| `models.py` | Data structures for evidence, conclusions and justifications |
| `strategies/` | Individual reasoning strategy implementations |

## Usage

```python
from core.reasoning import (
    ReasoningEngine,
    Evidence,
    ReasoningStrategy,
)
from datetime import datetime

# Create engine
engine = ReasoningEngine()

# Add evidence
evidence = Evidence(
    id="e1",
    content="Device shows power instability",
    source="sensor-data",
    source_type="sensor",
    timestamp=datetime.now(),
    confidence=0.9,
)
engine.add_evidence(evidence)

# Reason
conclusion, explanation = await engine.reason(
    question="What is the likely cause?",
    evidence_ids=["e1"],
    strategy=ReasoningStrategy.DEDUCTIVE,
)

print(f"Conclusion: {conclusion.statement}")
print(f"Confidence: {conclusion.confidence}")
print(f"Explanation: {explanation.summary}")
```

## Boundaries
- Reasoning capability only — no domain data ownership, no UI.
- May depend on `packages/*`; never on `apps/*`.
