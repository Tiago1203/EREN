# EPIC 9: Decision Engine

**Estado:** ✅ COMPLETO
**Fecha de inicio:** 2026-07-21
**Epic Owner:** Architecture Team
**Depende de:** EPIC 2, 3, 4, 5, 6, 7, 8

---

## Objetivo

El Decision Engine es el **punto donde toda la inteligencia converge**. Recibe información de todos los motores anteriores y construye la decisión clínica final.

---

## Filosofía Fundamental

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    AQUÍ FINALMENTE DECIDE                                    │
│                                                                              │
│  Opción A ─────────────────────────────────────────────────┐                 │
│  Opción B ─────────────────────────────────────────────► │ DECISIÓN FINAL   │
│  Opción C ─────────────────────────────────────────────► │                  │
│                                                          │ REEMPLAZAR       │
│  Reasoning + Evidence + Confidence + Rules + Safety ─────┤ SENSOR          │
│                                                          │                  │
│                                                          │ Motivos:         │
│                                                          │ • Mayor evidencia│
│                                                          │ • Menor riesgo   │
│                                                          │ • Cumple IEC     │
│                                                          │ • Confianza 94%  │
│                                                          └──────────────────┘
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DECISION ENGINE (EPIC 9)                              │
│                                                                              │
│  INPUT                                                                       
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ From ALL Previous Engines                                               │    │
│  │ ├── Reasoning Engine (EPIC 2) → Chains, Hypotheses                    │    │
│  │ ├── Evidence Engine (EPIC 3) → Evidence Bundle                        │    │
│  │ ├── Confidence Engine (EPIC 4) → Confidence Score                     │    │
│  │ ├── Explainability (EPIC 5) → Explanations                           │    │
│  │ ├── Rules Engine (EPIC 6) → Validation Result                        │    │
│  │ ├── Safety Engine (EPIC 7) → Safety Result                           │    │
│  │ └── Validation (EPIC 8) → Validation Result                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DECISION PIPELINE                                    │    │
│  │                                                                       │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │    │
│  │   │  Alternative │  │   Decision │  │   Action   │                │    │
│  │   │   Ranker    │  │    Score   │  │   Planner  │                │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                │    │
│  │          │               │               │                            │    │
│  │          └───────────────┼───────────────┘                            │    │
│  │                          ▼                                             │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │    │
│  │   │  Priority   │  │ Automation  │  │Recommendation│             │    │
│  │   │ Classifier  │  │  Evaluator  │  │  Generator  │              │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CLINICAL DECISION                                   │    │
│  │                                                                       │    │
│  │   {                                                                   │    │
│  │     "id": "decision_001",                                             │    │
│  │     "decision": "REPLACE_SENSOR",                                     │    │
│  │     "confidence": 0.94,                                               │    │
│  │     "priority": "HIGH",                                               │    │
│  │     "automation_level": "REQUIRES_REVIEW",                             │    │
│  │     "action_plan": [...],                                              │    │
│  │     "recommendations": [...],                                          │    │
│  │     "audit": {...}                                                    │    │
│  │   }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. Domain Models

```
Models
├── ClinicalDecision
│   ├── id: str
│   ├── timestamp: datetime
│   ├── decision: str
│   ├── confidence: float
│   ├── severity: Severity
│   ├── priority: Priority
│   ├── evidence: EvidenceBundle
│   ├── reasoning: ReasoningChain
│   ├── risks: list[Risk]
│   ├── alternatives: list[Alternative]
│   ├── recommended_actions: list[Action]
│   ├── validation_status: ValidationStatus
│   └── audit: AuditInfo
│
├── DecisionAlternative
│   ├── id: str
│   ├── option: str
│   ├── score: float
│   ├── evidence_count: int
│   ├── risk_level: RiskLevel
│   ├── confidence: float
│   └── ranking: int
│
├── DecisionScore
│   ├── total_score: float
│   ├── evidence_score: float
│   ├── confidence_score: float
│   ├── safety_score: float
│   ├── rules_score: float
│   └── ranking: int
│
├── DecisionPlan
│   ├── steps: list[PlanStep]
│   ├── estimated_duration: timedelta
│   ├── prerequisites: list[str]
│   └── safety_checks: list[str]
│
├── DecisionRecommendation
│   ├── recommendation: str
│   ├── reasoning: str
│   ├── priority: Priority
│   └── alternatives: list[str]
│
├── DecisionPriority
│   ├── CRITICAL → Immediate action
│   ├── HIGH → Action within 24h
│   ├── MEDIUM → Action within 7 days
│   ├── LOW → Action within 30 days
│   └── INFORMATIONAL → No action required
│
├── DecisionOutcome
│   ├── decision_id: str
│   ├── executed: bool
│   ├── outcome: str
│   ├── timestamp: datetime
│   └── operator: str
│
└── DecisionReport
    ├── decision_id: str
    ├── summary: str
    ├── details: dict
    └── recommendations: list[str]
```

### 2. Alternative Ranker

```
AlternativeRanker
├── ScoreCalculation
│   ├── Evidence weight (40%)
│   ├── Confidence weight (25%)
│   ├── Safety weight (20%)
│   └── Rules weight (15%)
├── RankingAlgorithm
│   ├── Option A: Score 82
│   ├── Option B: Score 96 ← BEST
│   └── Option C: Score 64
└── TieBreaking
    ├── Prefer safety
    ├── Prefer evidence
    └── Prefer confidence
```

### 3. Decision Scorer

```
DecisionScorer
├── ComponentScores
│   ├── Evidence Score (0-1)
│   ├── Confidence Score (0-1)
│   ├── Safety Score (0-1)
│   └── Rules Score (0-1)
├── WeightedSum
│   └── score = Σ(component × weight)
└── ScoreNormalization
    └── Final score 0-100
```

### 4. Action Planner

```
ActionPlanner
├── PlanGeneration
│   ├── Remove equipment from service
│   ├── Notify biomedical engineering
│   ├── Replace sensor
│   ├── Perform calibration
│   ├── Execute functional tests
│   └── Return equipment to service
├── StepDetails
│   ├── Step number
│   ├── Action description
│   ├── Estimated time
│   ├── Required personnel
│   └── Safety warnings
└── PlanValidation
    ├── Prerequisites met
    ├── Resources available
    └── Safety verified
```

### 5. Priority Classifier

```
PriorityClassifier
├── CRITICAL
│   ├── Patient safety immediate risk
│   ├── Equipment failure imminent
│   └── Regulatory compliance violation
│
├── HIGH
│   ├── Equipment performance degraded
│   ├── Preventive maintenance overdue
│   └── Risk of failure within 30 days
│
├── MEDIUM
│   ├── Performance optimization possible
│   ├── Preventive maintenance due
│   └── Minor safety concern
│
├── LOW
│   ├── General improvement
│   ├── Scheduled maintenance
│   └── Documentation update
│
└── INFORMATIONAL
    ├── Monitoring recommendation
    ├── Future consideration
    └── Observation only
```

### 6. Automation Evaluator

```
AutomationEvaluator
├── AUTO_APPROVED
│   ├── Low risk decision
│   ├── High confidence (>= 0.9)
│   ├── Standard procedure
│   └── Evidence strong
│
├── REQUIRES_REVIEW
│   ├── Moderate risk
│   ├── Confidence 0.5-0.9
│   ├── Non-standard procedure
│   └── New equipment type
│
└── BLOCKED
    ├── High risk
    ├── Low confidence (< 0.5)
    ├── Safety violation
    └── Rules violation
```

### 7. Recommendation Generator

```
RecommendationGenerator
├── TechnicalRecommendation
│   ├── "Replace pressure sensor"
│   ├── "Recalibrate monitor"
│   └── "Update firmware"
│
├── ClinicalRecommendation
│   ├── "Review maintenance protocol"
│   ├── "Verify pneumatic circuit"
│   └── "Schedule preventive maintenance"
│
└── PriorityRecommendation
    ├── Immediate actions
    ├── Short-term actions
    └── Long-term actions
```

### 8. Decision Recorder

```
DecisionRecorder
├── AuditLog
│   ├── Decision ID
│   ├── Timestamp
│   ├── Operator
│   ├── Reasoning version
│   ├── Knowledge version
│   ├── Evidence version
│   └── Confidence score
│
├── Persistence
│   ├── Database storage
│   ├── Audit trail
│   └── Compliance record
│
└── Retrieval
    ├── By ID
    ├── By date range
    ├── By equipment
    └── By operator
```

---

## Arquitectura de Archivos

```
core/
└── intelligence/
    └── decision/                               # EPIC 9: Decision Engine
        ├── __init__.py                    # Main module
        
        ├── models/                         # Domain Models
        │   ├── __init__.py
        │   ├── decision.py
        │   ├── alternative.py
        │   ├── plan.py
        │   └── priority.py
        
        ├── ranking/                        # Alternative Ranking
        │   ├── __init__.py
        │   └── ranker.py
        
        ├── scoring/                         # Decision Scoring
        │   ├── __init__.py
        │   └── scorer.py
        
        ├── planning/                       # Action Planning
        │   ├── __init__.py
        │   └── planner.py
        
        └── recording/                      # Audit Recording
            ├── __init__.py
            └── recorder.py
```

---

## Ejemplo: Decisión Completa

```python
# Input from all engines
input_data = {
    "alternatives": [
        {"option": "Recalibrate", "evidence": [...], "confidence": 0.82},
        {"option": "Replace Sensor", "evidence": [...], "confidence": 0.94},
        {"option": "Update Firmware", "evidence": [...], "confidence": 0.64},
    ],
    "safety_result": SafetyResult(decision="allow"),
    "rules_result": ValidationResult(is_compliant=True),
    "confidence": ConfidenceScore(total=0.89),
}

# Decision Engine Process
decision = await decision_engine.decide(input_data)

# Output: ClinicalDecision
print(decision)
# {
#     "id": "decision_20260721_001",
#     "decision": "REPLACE_SENSOR",
#     "confidence": 0.94,
#     "priority": "HIGH",
#     "automation_level": "REQUIRES_REVIEW",
#     "ranking": 1,
#     "action_plan": [
#         {"step": 1, "action": "Remove equipment from service"},
#         {"step": 2, "action": "Notify biomedical engineering"},
#         {"step": 3, "action": "Replace sensor"},
#         {"step": 4, "action": "Perform calibration"},
#         {"step": 5, "action": "Execute functional tests"},
#         {"step": 6, "action": "Return equipment to service"},
#     ],
#     "recommendations": [
#         "Replace pressure sensor",
#         "Schedule preventive maintenance",
#         "Verify pneumatic circuit",
#     ],
#     "audit": {
#         "timestamp": "2026-07-21T10:00:00Z",
#         "reasoning_version": "v2.1",
#         "knowledge_version": "v1.5",
#     }
# }
```

---

## Dependencias

| Dependencia | Tipo | Descripción |
|-------------|------|-------------|
| EPIC 2 | Requerida | Reasoning Engine |
| EPIC 3 | Requerida | Evidence Retrieval |
| EPIC 4 | Requerida | Confidence Engine |
| EPIC 5 | Requerida | Explainability |
| EPIC 6 | Requerida | Rules Engine |
| EPIC 7 | Requerida | Safety Engine |
| EPIC 8 | Requerida | Clinical Validation |

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

---

## Referencias

- [ADR-3090: Decision Engine Architecture](./adr/ADR-3090.md)
- [ADR-3091: Domain Models Design](./adr/ADR-3091.md)
- [ADR-3092: Ranking & Scoring Design](./adr/ADR-3092.md)
- [ADR-3093: Action Planning Design](./adr/ADR-3093.md)

---

*Document created: 2026-07-21*
*Last updated: 2026-07-21*
