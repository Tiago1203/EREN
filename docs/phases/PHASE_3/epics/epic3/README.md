# EPIC 3: Evidence Retrieval

**Estado:** ✅ COMPLETO
**Fecha de inicio:** 2026-07-21
**Epic Owner:** Architecture Team
**Depende de:** EPIC 2 (Reasoning Engine)

---

## Objetivo

Construir el sistema de recuperación y evaluación de evidencia para el razonamiento clínico. Cada razonamiento generado por EREN debe estar respaldado por evidencia verificable.

Este EPIC implementa:
- **Evidence Retrieval**: Búsqueda de evidencia desde múltiples fuentes
- **Evidence Bundle**: Agrupación de evidencia relacionada
- **Biomedical Rules Engine**: Motor de reglas tipo Drools para validación

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVIDENCE RETRIEVAL (EPIC 3)                               │
│                                                                              │
│  INPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Reasoning Output (from EPIC 2)                                         │    │
│  │ ├── Hypotheses                                                         │    │
│  │ ├── Reasoning Chains                                                   │    │
│  │ └── Diagnostics                                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EVIDENCE RETRIEVAL                                 │    │
│  │                                                                       │    │
│  │   Razonamiento ──► Busca evidencia                                     │    │
│  │         │              │                                               │    │
│  │         ▼              ▼                                               │    │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │    │
│  │   │Knowledge│    │ Manual  │    │  Norma  │    │Incidente│         │    │
│  │   │  Graph  │    │         │    │         │    │ similar │         │    │
│  │   └─────────┘    └─────────┘    └─────────┘    └─────────┘         │    │
│  │         │              │              │              │               │    │
│  │         └──────────────┴──────────────┴──────────────┘               │    │
│  │                              │                                          │    │
│  │                              ▼                                          │    │
│  │                      Evidence Bundle                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              BIOMEDICAL RULES ENGINE (Drools-style)                    │    │
│  │                                                                       │    │
│  │   ┌─────────────────────────────────────────────────────────────┐     │    │
│  │   │  CLINICAL RULES    │  ENGINEERING RULES  │  POLICIES      │     │    │
│  │   ├─────────────────────────────────────────────────────────────┤     │    │
│  │   │  Hospital Policies │  IEC / ISO / FDA    │  Manufacturer  │     │    │
│  │   │  Clinical Guild     │  AAMI / NFPA        │  Guidelines    │     │    │
│  │   └─────────────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  OUTPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ EvidenceBundle                                                       │    │
│  │ ├── Supporting Evidence (evidencia a favor)                          │    │
│  │ ├── Contradicting Evidence (evidencia en contra)                    │    │
│  │ ├── Confidence Score (puntuación de confianza)                   │    │
│  │ └── Rule Matches (reglas que se cumplen)                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. Evidence Retrieval Engine

```
EvidenceRetrieval
├── EvidenceSearcher
│   ├── KnowledgeGraphSearcher (EPIC 1)
│   ├── ManualSearcher (equipment manuals)
│   ├── StandardSearcher (IEC, ISO, etc.)
│   └── HistoricalSearcher (similar incidents)
├── EvidenceCollector
│   ├── SourceCollector
│   ├── EvidenceAggregator
│   └── RelevanceFilter
└── EvidenceRanker
    ├── QualityScorer
    ├── RelevanceScorer
    └── RecencyScorer
```

### 2. Evidence Bundle

```
EvidenceBundle
├── SupportingEvidence
│   ├── Evidence items
│   ├── Source attribution
│   └── Strength assessment
├── ContradictingEvidence
│   ├── Evidence items
│   ├── Source attribution
│   └── Weight assessment
└── EvidenceSummary
    ├── Overall assessment
    ├── Confidence level
    └── Recommendations
```

### 3. Biomedical Rules Engine (Drools-style)

```
BiomedicalRulesEngine
├── RuleRepository
│   ├── Clinical Rules
│   ├── Engineering Rules
│   ├── Hospital Policies
│   └── Manufacturer Guidelines
├── RuleEngine
│   ├── Pattern Matcher
│   ├── Condition Evaluator
│   └── Action Executor
└── RuleValidator
    ├── Syntax Validator
    ├── Conflict Detector
    └── Consistency Checker
```

---

## Ejemplo de Reglas

### Clinical Rules
```
RULE: "Ventilator Maintenance Required"
IF
  Equipment Type = "Ventilator"
  Last Calibration > 180 days
THEN
  Action = "Schedule Maintenance"
  Priority = HIGH
  Urgency = ROUTINE
```

### Engineering Rules
```
RULE: "Battery Replacement Required"
IF
  Battery Cycles > 500
THEN
  Action = "Replace Battery"
  Priority = HIGH
  Compliance = IEC 60601-1
```

### Safety Rules
```
RULE: "Critical Risk - Leakage Current"
IF
  Leakage Current > IEC 60601-1 limits
THEN
  Action = "IMMEDIATE REMOVAL"
  Priority = CRITICAL
  Urgency = EMERGENCY
```

---

## Arquitectura de Archivos

```
core/
└── intelligence/
    └── evidence/                          # EPIC 3: Evidence Retrieval
        ├── __init__.py
        │
        ├── retrieval/                    # Evidence Retrieval Engine
        │   ├── __init__.py
        │   ├── evidence_retriever.py
        │   ├── evidence_searcher.py
        │   ├── evidence_collector.py
        │   └── evidence_sources.py
        │
        ├── bundle/                      # Evidence Bundle
        │   ├── __init__.py
        │   ├── evidence_bundle.py
        │   ├── supporting_evidence.py
        │   └── evidence_summary.py
        │
        ├── scoring/                     # Evidence Scoring
        │   ├── __init__.py
        │   ├── quality_scorer.py
        │   ├── relevance_scorer.py
        │   └── confidence_calculator.py
        │
        ├── ranking/                    # Evidence Ranking
        │   ├── __init__.py
        │   ├── evidence_ranker.py
        │   └── ranking_algorithms.py
        │
        └── rules/                      # Biomedical Rules Engine
            ├── __init__.py
            ├── rules_engine.py
            ├── rule_repository.py
            ├── rule_types.py
            ├── clinical_rules.py
            ├── engineering_rules.py
            ├── policies_rules.py
            └── regulations/
                ├── __init__.py
                ├── iec_rules.py
                ├── iso_rules.py
                ├── fda_rules.py
                ├── aami_rules.py
                └── nfpa_rules.py
```

---

## Flujo de Datos

### Ejemplo: SpO2 Monitor

```
INPUT from EPIC 2:
├── Hypothesis: "Sensor malfunction (p=0.42)"
├── Reasoning Chain: [symptom] → [evidence] → [hypothesis]
└── Diagnostic: "SpO2 sensor issue"

│
▼ Evidence Retrieval
├── Knowledge Graph: Failure modes for pulse oximeter
├── Manuals: SpO2 sensor replacement procedures
├── Standards: IEC 60601-2-61 (pulse oximeters)
└── Historical: Similar incidents with SpO2 sensors

│
▼ Evidence Bundle
├── Supporting Evidence:
│   ├── "73% of similar cases were sensor issues" (Confidence: 0.85)
│   ├── "Sensor age > 2000 hours" (Evidence: maintenance_log)
│   └── "IEC 60601-2-61 requires calibration < 180 days" (Standard)
├── Contradicting Evidence:
│   └── "Last calibration was 30 days ago" (Confidence: 0.6)
└── Overall Confidence: 0.78

│
▼ Rules Engine
├── MATCH: "Equipment Age > Threshold" → Maintenance Required
├── MATCH: "Sensor Hours > Limit" → Replace Probe
└── NO MATCH: Safety critical (no leakage current issue)

OUTPUT:
├── EvidenceBundle with confidence 0.78
├── Rule matches: 2
└── Recommendations: ["Replace sensor probe", "Verify calibration"]
```

---

## Dependencias

| Dependencia | Tipo | Descripción |
|-------------|------|-------------|
| EPIC 0 | Requerida | Foundation (DTOs, Models) |
| EPIC 1 | Requerida | Knowledge Graph |
| EPIC 2 | Requerida | Reasoning Engine |

---

## Estado del Proyecto

| EPIC | Estado |
|------|--------|
| EPIC 0 | ✅ COMPLETO |
| EPIC 1 | ✅ COMPLETO |
| EPIC 2 | ✅ COMPLETO |
| EPIC 3 | ✅ COMPLETO |

---

## Referencias

- [ADR-3030: Evidence Retrieval Architecture](./adr/ADR-3030.md)
- [ADR-3031: Evidence Bundle Design](./adr/ADR-3031.md)
- [ADR-3032: Biomedical Rules Engine Design](./adr/ADR-3032.md)
- [ADR-3033: Regulations Integration Design](./adr/ADR-3033.md)

---

*Document created: 2026-07-21*
*Last updated: 2026-07-21*
