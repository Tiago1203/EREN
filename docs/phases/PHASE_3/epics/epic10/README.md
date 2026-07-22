# EPIC 10: Learning Engine

**Estado:** ✅ COMPLETO
**Fecha de inicio:** 2026-07-21
**Epic Owner:** Architecture Team
**Depende de:** EPIC 1-9 (todos los anteriores)

---

## Objetivo

El Learning Engine es el **cierre del ciclo de inteligencia**. No razona, no responde usuarios, no genera prompts. **Aprende de los resultados**.

---

## Filosofía Fundamental

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│              EL CICLO SE CIERRA AQUÍ                                          │
│                                                                              │
│  Knowledge ──► Reasoning ──► Evidence ──► Confidence ──► Explainability    │
│       ▲                                                                   │
│       │                                                                   │
│       │              Learning Engine                                          │
│       │                                                                   │
│       └──── Knowledge (actualizado con experiencia) ◄────                   │
│                                                                              │
│  Knowledge ◄── Reasoning ◄── Evidence ◄── Confidence ◄── Explainability    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LEARNING ENGINE (EPIC 10)                                  │
│                                                                              │
│  INPUT                                                                       
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ From Decision Engine (EPIC 9)                                           │    │
│  │ ├── Clinical Decision                                                   │    │
│  │ ├── Recommended Actions                                                 │    │
│  │ ├── Confidence Score                                                    │    │
│  │ └── Reasoning Chain                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    LEARNING PIPELINE                                     │    │
│  │                                                                       │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │    │
│  │   │  Outcome   │  │  Feedback  │  │  Experience │                │    │
│  │   │ Collector  │  │  Manager   │  │ Repository  │                │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                │    │
│  │          │               │               │                            │    │
│  │          └───────────────┼───────────────┘                            │    │
│  │                          ▼                                             │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │    │
│  │   │  Pattern   │  │  Similarity │  │  Knowledge  │              │    │
│  │   │ Discovery  │  │  Analyzer   │  │  Updater    │              │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘              │    │
│  │          │               │               │                            │    │
│  │          └───────────────┼───────────────┘                            │    │
│  │                          ▼                                             │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │    │
│  │   │ Confidence │  │    Rule    │  │Recommendation│             │    │
│  │   │  Trainer   │  │ Optimizer  │  │   Scorer    │              │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    LEARNING PACKAGE                                     │    │
│  │                                                                       │    │
│  │   {                                                                   │    │
│  │     "new_knowledge": [...],                                             │    │
│  │     "updated_confidence": {...},                                       │    │
│  │     "new_patterns": [...],                                             │    │
│  │     "suggested_rules": [...],                                          │    │
│  │     "recommendation_scores": [...],                                    │    │
│  │     "similar_cases": [...],                                            │    │
│  │     "experience_records": [...],                                        │    │
│  │     "learning_metrics": {...}                                           │    │
│  │   }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              FEEDS BACK TO KNOWLEDGE ENGINE                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. Outcome Collector

```
OutcomeCollector
├── Decision Outcome
│   ├── Decision ID
│   ├── Recommended Action
│   ├── Actual Outcome
│   │   ├── SUCCESS
│   │   ├── PARTIAL_SUCCESS
│   │   ├── FAILURE
│   │   └── UNKNOWN
│   └── Evidence of Outcome
│
├── Outcome Verification
│   ├── Was recommendation followed?
│   ├── Did it solve the problem?
│   └── Side effects observed?
│
└── Outcome Recording
    ├── Timestamp
    ├── Operator who executed
    └── Equipment status after
```

### 2. Feedback Manager

```
FeedbackManager
├── Feedback Sources
│   ├── Biomedical Engineer
│   ├── Hospital Administrator
│   ├── Technician
│   ├── Clinical Engineer
│   └── External System
│
├── Feedback Types
│   ├── CORRECT - Recommendation was accurate
│   ├── INCORRECT - Recommendation was wrong
│   ├── PARTIALLY_CORRECT - Some aspects correct
│   ├── MISSING_CONTEXT - More info needed
│   └── NEEDS_REVIEW - Requires human validation
│
└── Feedback Processing
    ├── Feedback validation
    ├── Sentiment analysis
    └── Priority assignment
```

### 3. Experience Repository

```
ExperienceRepository
├── Experience Cases
│   ├── Device
│   ├── Symptoms
│   ├── Diagnosis
│   ├── Decision Made
│   ├── Outcome
│   ├── Engineer Feedback
│   ├── Confidence at Decision Time
│   └── Actual Confidence (after outcome)
│
├── Case Storage
│   ├── Indexed by device type
│   ├── Indexed by symptoms
│   ├── Indexed by outcome
│   └── Indexed by feedback
│
└── Case Retrieval
    ├── Find similar cases
    ├── Find opposite outcomes
    └── Find feedback patterns
```

### 4. Pattern Discovery

```
PatternDiscovery
├── Time Patterns
│   ├── Seasonal failures
│   ├── Weekday/weekend patterns
│   └── Hourly patterns
│
├── Device Patterns
│   ├── Model-specific failures
│   ├── Batch/lot failures
│   └── Age-related failures
│
├── Environmental Patterns
│   ├── Temperature correlation
│   ├── Humidity correlation
│   └── Usage patterns
│
└── Recommendation Patterns
    ├── Successful recommendation types
    └── Failed recommendation types
```

### 5. Similarity Analyzer

```
SimilarityAnalyzer
├── Case Similarity
│   ├── Device similarity
│   ├── Symptom similarity
│   ├── Context similarity
│   └── Outcome similarity
│
├── Similarity Metrics
│   ├── Jaccard similarity
│   ├── Cosine similarity
│   └── Weighted similarity
│
└── Similarity Use Cases
    ├── Find similar historical cases
    ├── Predict outcome based on similarity
    └── Improve reasoning chains
```

### 6. Knowledge Updater

```
KnowledgeUpdater
├── Knowledge Updates
│   ├── New device failure modes
│   ├── New symptom-diagnosis mappings
│   ├── New maintenance procedures
│   └── New device relationships
│
├── Update Validation
│   ├── Source credibility check
│   ├── Consistency check
│   └── Human approval for major updates
│
└── Update Types
    ├── Minor (automatic)
    ├── Moderate (review required)
    └── Major (human approval required)
```

### 7. Confidence Trainer

```
ConfidenceTrainer
├── Confidence Adjustments
│   ├── If outcome = SUCCESS and confidence < 0.9
│   │   → Increase confidence
│   │
│   ├── If outcome = FAILURE and confidence > 0.7
│   │   → Decrease confidence
│   │
│   └── If outcome = PARTIAL and confidence = X
│       → Adjust proportionally
│
├── Training Factors
│   ├── Number of successful cases
│   ├── Number of failed cases
│   ├── Recency of cases
│   └── Feedback quality
│
└── Calibration
    ├── Confidence should reflect actual accuracy
    └── Periodic recalibration
```

### 8. Rule Optimizer

```
RuleOptimizer
├── Rule Discovery
│   ├── Analyze successful vs failed decisions
│   ├── Identify new rule conditions
│   └── Suggest rule modifications
│
├── Example
│   ├── Before: Battery > 500 cycles
│   ├── After: Battery > 420 cycles (Hospital data shows earlier failures)
│   └── Validation: Requires human approval
│
├── Rule Categories
│   ├── Equipment-specific rules
│   ├── Hospital-specific rules
│   ├── Department-specific rules
│   └── Universal rules
│
└── Rule Validation
    ├── Statistical significance check
    ├── Human review requirement
    └── Gradual rollout
```

### 9. Recommendation Scorer

```
RecommendationScorer
├── Score Components
│   ├── Success rate for similar cases
│   ├── Average confidence when recommended
│   ├── User feedback score
│   └── Pattern consistency
│
├── Score Update
│   ├── Recommendation + SUCCESS → +score
│   ├── Recommendation + FAILURE → -score
│   └── Recommendation + PARTIAL → ±score based on ratio
│
└── Score Thresholds
    ├── High confidence threshold: 0.85
    ├── Medium confidence threshold: 0.60
    └── Low confidence threshold: 0.40
```

### 10. Continuous Learning Pipeline

```
ContinuousLearningPipeline
├── Learning Cycle
│   ├── Collect outcomes
│   ├── Process feedback
│   ├── Discover patterns
│   ├── Update knowledge
│   ├── Train confidence
│   └── Optimize rules
│
├── Distribution
│   ├── Knowledge Engine (EPIC 1)
│   ├── Reasoning Engine (EPIC 2)
│   ├── Confidence Engine (EPIC 4)
│   └── Decision Engine (EPIC 9)
│
└── Monitoring
    ├── Learning metrics
    ├── Improvement tracking
    └── Drift detection
```

---

## Arquitectura de Archivos

```
core/
└── intelligence/
    └── learning/                             # EPIC 10: Learning Engine
        ├── __init__.py                    # Main module
        
        ├── outcomes/                       # Outcome Collection
        │   ├── __init__.py
        │   └── collector.py
        
        ├── feedback/                       # Feedback Management
        │   ├── __init__.py
        │   └── manager.py
        
        ├── experience/                     # Experience Repository
        │   ├── __init__.py
        │   └── repository.py
        
        ├── patterns/                       # Pattern Discovery
        │   ├── __init__.py
        │   └── discovery.py
        
        └── updates/                        # Knowledge Updates
            ├── __init__.py
            └── updater.py
```

---

## Learning Package

```python
@dataclass
class LearningPackage:
    """Package of learnings to distribute."""
    
    # New knowledge discovered
    new_knowledge: list[KnowledgeUpdate]
    
    # Confidence adjustments
    updated_confidence: list[ConfidenceUpdate]
    
    # New patterns found
    new_patterns: list[Pattern]
    
    # Rule suggestions
    suggested_rules: list[RuleSuggestion]
    
    # Recommendation scores
    recommendation_scores: list[RecommendationScore]
    
    # Similar cases for future reference
    similar_cases: list[SimilarCase]
    
    # Experience records
    experience_records: list[ExperienceRecord]
    
    # Metrics
    learning_metrics: LearningMetrics
```

---

## Ejemplo: Ciclo Completo

```
1. DECISION MADE
   Decision: "Replace SpO2 sensor"
   Confidence: 0.87

2. OUTCOME COLLECTED
   Outcome: SUCCESS
   Problem solved: YES
   Time to resolution: 2 hours

3. FEEDBACK RECEIVED
   Feedback: CORRECT
   Engineer: "Sensor replacement was appropriate"

4. PATTERN DISCOVERED
   Pattern: SpO2 sensors fail after 6 months in high humidity

5. KNOWLEDGE UPDATED
   New fact: "SpO2 sensors in Unit 3 require 4-month calibration"

6. CONFIDENCE UPDATED
   Old confidence for sensor replacement: 0.87
   New confidence for sensor replacement: 0.92

7. LEARNING PACKAGE DISTRIBUTED
   → Knowledge Engine
   → Reasoning Engine
   → Confidence Engine
   → Decision Engine

8. NEXT DECISION (improved)
   Decision: "Replace SpO2 sensor"
   Confidence: 0.92 ← IMPROVED
```

---

## Dependencias

| Dependencia | Tipo | Descripción |
|-------------|------|-------------|
| EPIC 1 | Requerida | Biomedical Knowledge Engine |
| EPIC 2 | Requerida | Reasoning Engine |
| EPIC 3 | Requerida | Evidence Retrieval |
| EPIC 4 | Requerida | Confidence Engine |
| EPIC 9 | Requerida | Decision Engine |

**Nota:** Depende de TODOS los EPICs anteriores - es el único que cierra el ciclo.

---

## Estado del Proyecto

| EPIC | Estado |
|------|--------|
| EPIC 0 | ✅ COMPLETO |
| EPIC 1 | ✅ COMPLETO |
| EPIC 2 | ✅ COMPLETO |
| EPIC 3 | ✅ COMPLETO |
| EPIC 4 | ✅ COMPLETO |
| EPIC 5 | ✅ COMPLETO |
| EPIC 6 | ✅ COMPLETO |
| EPIC 7 | ✅ COMPLETO |
| EPIC 8 | ✅ COMPLETO |
| EPIC 9 | ✅ COMPLETO |
| EPIC 10 | ✅ COMPLETO |

---

## Referencias

- [ADR-3100: Learning Engine Architecture](./adr/ADR-3100.md)
- [ADR-3101: Outcome Collection Design](./adr/ADR-3101.md)
- [ADR-3102: Feedback & Experience Design](./adr/ADR-3102.md)
- [ADR-3103: Pattern Discovery Design](./adr/ADR-3103.md)

---

*Document created: 2026-07-21*
*Last updated: 2026-07-21*
