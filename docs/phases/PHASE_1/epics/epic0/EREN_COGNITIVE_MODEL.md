# EREN Cognitive Model
## How EREN Thinks

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial (EXPERIMENTAL) |
| 1.1 | 2026-07-16 | Architecture Board | Frozen for EPIC 4 AI Core — formal contracts added |

---

## Overview

EREN's cognitive model is inspired by human cognition, not by pipeline processing. It is a **network** of capabilities that influence each other, not a **sequence** of steps.

**Status: FROZEN ✅** — Ready for EPIC 4 (AI Core) implementation.

All 11 capabilities are now formal contracts with:
- Protocol definitions (interface)
- Input/output contracts
- Implementation hints
- EPIC alignment

```
                Memory
            ↗          ↖
Knowledge ← Context → Reasoning
       ↘            ↙
        Trust   Risk
             ↓
         Decision
             ↓
      Explanation
             ↓
         Learning
             ↺
```

---

## The Cognitive Network

### Core Principle: Everything Affects Everything

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   Memory ←───────→ Reasoning                                │
│      ↑                   ↑                                 │
│      │                   │                                 │
│      ↓                   │                                 │
│   Knowledge ←──────→ Context                                │
│      ↑                   ↑                                 │
│      │                   │                                 │
│      └─────────┬─────────┘                                 │
│                ↓                                           │
│             Trust                                          │
│                ↓                                           │
│              Risk                                           │
│                ↓                                           │
│           Decision                                         │
│                ↓                                           │
│          Explanation                                        │
│                ↓                                           │
│            Learning ─────────────→ Memory                   │
│                                                       ↑     │
│                        (cycle continues)                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Cognitive Capabilities (FROZEN ✅)

**All 11 capabilities are formal contracts. Implementation is now ready for EPIC 4 (AI Core).**

### Capability Map to EPIC

| Capability | EPIC | Phase | Priority |
|------------|------|-------|----------|
| Perceive | EPIC 6 | Integrations | Critical |
| Remember | EPIC 4 | AI Core | Critical |
| Know | EPIC 4 | AI Core | Critical |
| Trust | EPIC 4 | AI Core | Critical |
| AssessRisk | EPIC 5 | Clinical Intelligence | Critical |
| Reason | EPIC 4 | AI Core | Critical |
| Plan | EPIC 5 | Clinical Intelligence | High |
| Decide | EPIC 4 | AI Core | Critical |
| Explain | EPIC 4 | AI Core | Critical |
| Learn | EPIC 9 | Machine Learning | High |
| Reflect | EPIC 4 | AI Core | Medium |

---

### 1. Perceive

**What it does:** Captures signals from the environment.

```python
class Perceive(Protocol):
    """Signal capture and interpretation."""
    
    async def perceive_signal(signal: Signal) -> Perception
    async def perceive_context(context: Context) -> ContextSnapshot
    async def perceive_alert(alert: Alert) -> AlertAssessment
```

**Inputs:** Raw data from devices, users, systems
**Outputs:** Structured perceptions

### 2. Remember

**What it does:** Stores and retrieves information from memory.

```python
class Remember(Protocol):
    """Memory operations."""
    
    async def encode(experience: Experience) -> MemoryRef
    async def retrieve(query: Query) -> MemoryResult
    async def consolidate(memories: list[MemoryRef]) -> None
```

**Inputs:** Experiences, outcomes, context
**Outputs:** Memory references for retrieval

### 3. Know

**What it does:** Manages structured knowledge.

```python
class Know(Protocol):
    """Knowledge management."""
    
    async def query_knowledge(question: str) -> KnowledgeResult
    async def add_fact(fact: Fact) -> None
    async def get_evidence(topic: Topic) -> list[Evidence]
```

**Inputs:** Queries, facts, evidence
**Outputs:** Knowledge results, evidence

### 4. Trust

**What it does:** Evaluates credibility and reliability.

```python
class Trust(Protocol):
    """Trust evaluation."""
    
    async def evaluate_source(source: Source) -> TrustScore
    async def evaluate_evidence(evidence: Evidence) -> TrustScore
    async def get_trust_context(entity: Entity) -> TrustContext
```

**Inputs:** Sources, evidence, credentials
**Outputs:** Trust scores and confidence levels

### 5. Assess Risk

**What it does:** Evaluates potential harms and their likelihood.

```python
class AssessRisk(Protocol):
    """Risk assessment."""
    
    async def evaluate_risk(scenario: Scenario) -> RiskAssessment
    async def identify_hazards(situation: Situation) -> list[Hazard]
    async def recommend_mitigation(risk: Risk) -> Mitigation
```

**Inputs:** Situations, scenarios, decisions
**Outputs:** Risk scores, hazard identification, mitigations

### 6. Reason

**What it does:** Generates inferences from evidence.

```python
class Reason(Protocol):
    """Reasoning engine."""
    
    async def infer(evidence: list[Evidence]) -> list[Inference]
    async def explain(inference: Inference) -> Explanation
    async def validate_reasoning(chain: ReasoningChain) -> Validation
```

**Inputs:** Evidence, context, trust levels
**Outputs:** Inferences, explanations, confidence

### 7. Plan

**What it does:** Generates action plans.

```python
class Plan(Protocol):
    """Planning engine."""
    
    async def create_plan(goal: Goal, constraints: Constraints) -> Plan
    async def evaluate_plan(plan: Plan) -> PlanAssessment
    async def adapt_plan(plan: Plan, feedback: Feedback) -> Plan
```

**Inputs:** Goals, constraints, resources
**Outputs:** Actionable plans with contingencies

### 8. Decide

**What it does:** Selects among options.

```python
class Decide(Protocol):
    """Decision engine."""
    
    async def evaluate_options(options: list[Option]) -> Decision
    async def make_recommendation(options: list[Option]) -> Recommendation
    async def explain_decision(decision: Decision) -> Explanation
```

**Inputs:** Options, preferences, risk tolerance, constraints
**Outputs:** Decisions with rationale

### 9. Explain

**What it does:** Generates human-understandable explanations.

```python
class Explain(Protocol):
    """Explanation engine."""
    
    async def explain_reasoning(inference: Inference) -> Explanation
    async def explain_decision(decision: Decision) -> Explanation
    async def provide_evidence(claim: Claim) -> EvidenceSummary
```

**Inputs:** Reasoning chains, decisions, evidence
**Outputs:** Natural language explanations

### 10. Learn

**What it does:** Improves from outcomes.

```python
class Learn(Protocol):
    """Learning engine."""
    
    async def learn_from_outcome(outcome: Outcome) -> Learning
    async def update_knowledge(new_fact: Fact) -> None
    async def adjust_trust(source: Source, outcome: Outcome) -> TrustScore
```

**Inputs:** Outcomes, decisions, feedback
**Outputs:** Updated knowledge, adjusted trust, improved models

### 11. Reflect

**What it does:** Examines and improves its own reasoning.

```python
class Reflect(Protocol):
    """Metacognition."""
    
    async def evaluate_reasoning(process: ReasoningProcess) -> Reflection
    async def identify_bias(reasoning: Reasoning) -> list[Bias]
    async def recommend_improvement(reflection: Reflection) -> Suggestion
```

**Inputs:** Past reasoning processes
**Outputs:** Insights about reasoning quality

---

## The Decision Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  1. SITUATION ASSESSMENT                                     │
│     └─ What is happening?                                    │
│     └─ What is the clinical context?                        │
│     └─ What devices are involved?                           │
│                                                              │
│  2. KNOWLEDGE RETRIEVAL                                      │
│     └─ What does the evidence say?                          │
│     └─ What are similar past cases?                         │
│     └─ What guidelines apply?                              │
│                                                              │
│  3. TRUST EVALUATION                                         │
│     └─ How trustworthy is this source?                      │
│     └─ Is this information current?                         │
│     └─ Is this consistent with other sources?               │
│                                                              │
│  4. RISK ASSESSMENT                                          │
│     └─ What could go wrong?                                  │
│     └─ How likely? How severe?                              │
│     └─ What is the risk if we do nothing?                   │
│                                                              │
│  5. REASONING                                                │
│     └─ What conclusions can we draw?                        │
│     └─ What are the alternatives?                           │
│     └─ What assumptions are we making?                     │
│                                                              │
│  6. DECISION                                                 │
│     └─ What is the recommendation?                          │
│     └─ What is the confidence level?                        │
│     └─ What are the trade-offs?                             │
│                                                              │
│  7. EXPLANATION                                              │
│     └─ Why this recommendation?                             │
│     └─ What evidence supports it?                           │
│     └─ What alternatives exist?                             │
│                                                              │
│  8. MONITORING                                              │
│     └─ Is the situation changing?                           │
│     └─ Should we revisit the decision?                       │
│     └─ What can we learn?                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Cross-Capability Influences

### Memory → Everything

```
Memory provides:
- Past cases → informs Reasoning
- Historical outcomes → adjusts Trust
- Previous decisions → biases current Decisions
- Learned patterns → shapes Know
```

### Knowledge → Reasoning

```
Knowledge provides:
- Evidence base → feeds Reasoning
- Guidelines → constrain Plans
- Facts → support Decisions
- Definitions → clarify Context
```

### Trust → Reasoning

```
Trust affects:
- Which evidence is weighted heavily
- Which sources are consulted
- How uncertainty is interpreted
- How confident to be in conclusions
```

### Risk → Decision

```
Risk affects:
- Which options are viable
- How conservative the recommendation
- Whether to escalate to human
- How to frame the explanation
```

### Learning → Memory

```
Learning updates:
- Memory consolidation
- Trust adjustments
- Knowledge additions
- Pattern recognition
```

---

## Example: Clinical Decision

```
Situation: "ICU patient on ventilator showing irregular readings"

┌─────────────────────────────────────────────────────────────┐
│ 1. PERCEIVE                                                 │
│    Signal: Ventilator alarm, SpO2 89%, HR 112              │
│    Context: ICU, patient ID 12345, ventilated x24h        │
│                                                              │
│ 2. REMEMBER                                                 │
│    Similar case: Patient 12340 (3 days ago)                │
│    Resolution: Secretions, suctioning helped                │
│                                                              │
│ 3. KNOW                                                     │
│    Evidence: Literature on ventilator alarms                │
│    Guidelines: AACN protocols for ventilated patients       │
│                                                              │
│ 4. TRUST                                                    │
│    Monitor readings: HIGH trust (calibrated, recent)        │
│    Similar case: MODERATE trust (different patient)         │
│    Guidelines: HIGH trust (evidence-based)                  │
│                                                              │
│ 5. ASSESS RISK                                              │
│    If delayed: MODERATE-HIGH risk (patient safety)         │
│    If suctioning: LOW risk                                  │
│    If wrong intervention: HIGH risk                         │
│                                                              │
│ 6. REASON                                                   │
│    Inference: Likely secretions or tube issue               │
│    Confidence: 75% (moderate uncertainty)                   │
│    Alternatives: Check tube, suction, adjust settings       │
│                                                              │
│ 7. DECIDE                                                    │
│    Recommendation: Assess tube position, consider suctioning │
│    Confidence: 75%                                          │
│    Escalation: If no improvement in 5 min, escalate to MD   │
│                                                              │
│ 8. EXPLAIN                                                   │
│    "Based on similar cases and guidelines, the most likely │
│    cause is secretions. However, I'm only 75% confident.   │
│    Recommendation: Assess tube, suction. If no improvement  │
│    in 5 minutes, escalate to physician."                     │
│                                                              │
│ 9. MONITOR                                                  │
│    Track: SpO2, HR, response to intervention               │
│    Learn: Did this intervention work?                       │
│    Update: Adjust future confidence based on outcome        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Principles

### 1. Capabilities Are Independent but Connected

```python
# Each capability can be replaced independently
# But they all share the cognitive state

class CognitiveRuntime:
    perceive: Perceive
    remember: Remember
    know: Know
    trust: Trust
    assess_risk: AssessRisk
    reason: Reason
    plan: Plan
    decide: Decide
    explain: Explain
    learn: Learn
    reflect: Reflect
```

### 2. State Is Shared via Cognitive Context

```python
@dataclass
class CognitiveState:
    perception: Perception | None
    memories: list[MemoryRef]
    knowledge: KnowledgeContext
    trust_scores: dict[Source, TrustScore]
    risk_assessment: RiskAssessment | None
    reasoning_chain: ReasoningChain
    pending_decision: Decision | None
```

### 3. Trust and Risk Are Always Computed

```
Every inference must include:
- Trust level of supporting evidence
- Risk assessment of conclusion
- Confidence based on both
```

### 4. Explanations Are First-Class

```
Every recommendation must have:
- The conclusion
- Supporting evidence
- Trust in that evidence
- Risk if wrong
- Alternative options
```

---

*EREN Cognitive Model v1.1 — FROZEN for EPIC 4 AI Core*
*Architecture Board - 2026-07-16*
