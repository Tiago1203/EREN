# EPIC 4: Confidence Engine

**Estado:** ✅ COMPLETO
**Fecha de inicio:** 2026-07-21
**Epic Owner:** Architecture Team
**Depende de:** EPIC 2 (Reasoning Engine), EPIC 3 (Evidence Retrieval)

---

## Objetivo

Construir el módulo de confianza que permite a EREN calcular y comunicar su nivel de certeza sobre sus propios razonamientos. El Confidence Engine responde a la pregunta fundamental:

> **"¿Qué tan seguro está EREN de su respuesta?"**

Este módulo es crítico porque permite a EREN decir **"No estoy seguro"** cuando no tiene suficiente evidencia, en lugar de inventar respuestas incorrectas.

---

## Filosofía

El Confidence Engine implementa un principio fundamental de EREN:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│   "EREN aprende a decir 'No estoy seguro.'                        │
│    En vez de inventar."                                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CONFIDENCE ENGINE (EPIC 4)                             │
│                                                                              │
│  INPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ From Reasoning + Evidence (EPIC 2 + EPIC 3)                            │    │
│  │ ├── Hypotheses                                                         │    │
│  │ ├── Evidence Bundle                                                    │    │
│  │ ├── Reasoning Chains                                                   │    │
│  │ └── Rule Matches                                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CONFIDENCE COMPONENTS                              │    │
│  │                                                                       │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │    │
│  │   │ Confidence  │  │    Risk     │  │   Quality   │                │    │
│  │   │ Calculator  │  │  Assessor   │  │  Evaluator │                │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                │    │
│  │          │               │               │                            │    │
│  │          └───────────────┼───────────────┘                            │    │
│  │                          │                                            │    │
│  │   ┌─────────────┐  ┌─────────────┐                                  │    │
│  │   │  Coverage  │  │  Ambiguity   │                                  │    │
│  │   │  Analyzer  │  │   Detector   │                                  │    │
│  │   └─────────────┘  └─────────────┘                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  OUTPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ ConfidenceScore                                                         │    │
│  │ ├── Overall Confidence (0-100%)                                        │    │
│  │ ├── Component Scores                                                    │    │
│  │ ├── Uncertainty Factors                                                │    │
│  │ ├── Recommendations                                                    │    │
│  │ └── "I'm not sure" indicator                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. Confidence Calculator

```
ConfidenceCalculator
├── EvidenceBasedCalculator
│   ├── Evidence weight calculation
│   ├── Source quality adjustment
│   └── Confirmation bias correction
├── KnowledgeBasedCalculator
│   ├── Knowledge coverage
│   ├── Knowledge quality
│   └── Knowledge recency
├── ReasoningBasedCalculator
│   ├── Chain strength
│   ├── Inference validity
│   └── Conclusion support
└── EnsembleCalculator
    ├── Weighted combination
    └── Uncertainty propagation
```

**Responsabilidades:**
- Calcular puntuación de confianza 0-100%
- Combinar múltiples fuentes de evidencia
- Propagar incertidumbre

### 2. Risk Assessor

```
RiskAssessor
├── RiskIdentification
│   ├── Clinical risk factors
│   ├── Safety risk factors
│   └── Operational risk factors
├── RiskQuantification
│   ├── Probability assessment
│   ├── Severity assessment
│   └── Risk matrix calculation
└── RiskCommunication
    ├── Risk level (LOW/MEDIUM/HIGH/CRITICAL)
    └── Risk justification
```

**Responsabilidades:**
- Evaluar riesgos asociados al razonamiento
- Cuantificar probabilidad e impacto
- Comunicar niveles de riesgo

### 3. Quality Evaluator

```
QualityEvaluator
├── EvidenceQuality
│   ├── Source credibility
│   ├── Information completeness
│   └── Temporal relevance
├── ReasoningQuality
│   ├── Logical validity
│   ├── Premise support
│   └── Conclusion consistency
└── OutputQuality
    ├── Clarity score
    ├── Actionability score
    └── Completeness score
```

**Responsabilidades:**
- Evaluar calidad de evidencia y razonamiento
- Identificar gaps de calidad
- Proponer mejoras

### 4. Coverage Analyzer

```
CoverageAnalyzer
├── DomainCoverage
│   ├── Topics covered
│   ├── Topics missing
│   └── Coverage percentage
├── EvidenceCoverage
│   ├── Relevant evidence found
│   ├── Evidence gaps
│   └── Coverage completeness
└── ReasoningCoverage
    ├── Alternatives considered
    ├── Edge cases covered
    └── Potential blind spots
```

**Responsabilidades:**
- Analizar qué tan completa es la información disponible
- Identificar gaps de cobertura
- Cuantificar porcentaje de cobertura

### 5. Ambiguity Detector

```
AmbiguityDetector
├── SemanticAmbiguity
│   ├── Multiple interpretations
│   ├── Vague terminology
│   └── Context dependence
├── EvidentialAmbiguity
│   ├── Conflicting evidence
│   ├── Incomplete evidence
│   └── Inconsistent facts
└── ReasoningAmbiguity
    ├── Multiple valid conclusions
    ├── Unexplained variance
    └── Unresolved uncertainty
```

**Responsabilidades:**
- Detectar ambiguüedad en el razonamiento
- Identificar evidencia conflicting
- Señalar cuando hay múltiples interpretaciones válidas

---

## Ejemplo: SpO2 Monitor

### Alta Confianza (92%)

```
INPUT:
├── Maintenance history complete
├── Knowledge available
├── Evidence confirmed
└── Calibration within 180 days

CALCULATION:
├── Evidence Weight: 0.95 (high quality sources)
├── Knowledge Coverage: 0.90 (well documented)
├── Reasoning Strength: 0.92 (strong chain)
└── Risk Level: LOW

OUTPUT:
Confidence Score: 92%
"I'm confident that the SpO2 sensor needs replacement."
```

### Baja Confianza (31%)

```
INPUT:
├── No calibration history
├── Few similar incidents
├── Low evidence
└── Multiple possible causes

CALCULATION:
├── Evidence Weight: 0.30 (low quality)
├── Knowledge Coverage: 0.25 (limited knowledge)
├── Reasoning Strength: 0.40 (weak chain)
└── Risk Level: MEDIUM

OUTPUT:
Confidence Score: 31%
"I'm not sure what's causing the SpO2 issue. More investigation needed."
```

---

## Arquitectura de Archivos

```
core/
└── intelligence/
    └── confidence/                         # EPIC 4: Confidence Engine
        ├── __init__.py
        │
        ├── calculator/                    # Confidence Calculator
        │   ├── __init__.py
        │   ├── confidence_calculator.py
        │   ├── evidence_calculator.py
        │   ├── knowledge_calculator.py
        │   └── reasoning_calculator.py
        │
        ├── risk/                         # Risk Assessor
        │   ├── __init__.py
        │   ├── risk_assessor.py
        │   ├── risk_identifier.py
        │   └── risk_quantifier.py
        │
        ├── quality/                      # Quality Evaluator
        │   ├── __init__.py
        │   ├── quality_evaluator.py
        │   ├── evidence_quality.py
        │   └── reasoning_quality.py
        │
        ├── coverage/                    # Coverage Analyzer
        │   ├── __init__.py
        │   ├── coverage_analyzer.py
        │   ├── domain_coverage.py
        │   └── evidence_coverage.py
        │
        ├── ambiguity/                  # Ambiguity Detector
        │   ├── __init__.py
        │   ├── ambiguity_detector.py
        │   ├── semantic_ambiguity.py
        │   └── evidential_ambiguity.py
        │
        └── models/                     # Shared Models
            ├── __init__.py
            ├── confidence_score.py
            └── confidence_result.py
```

---

## Flujo de Integración

```
                    ┌─────────────────┐
                    │   EPIC 2        │
                    │ Reasoning Engine │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   EPIC 3        │
                    │Evidence Retrieval│
                    └────────┬────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                    CONFIDENCE ENGINE (EPIC 4)                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Input: Hypotheses, Evidence, Chains, Rules                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                      │
│      ┌──────────────────────┼──────────────────────┐             │
│      ▼                      ▼                      ▼             │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐            │
│  │Confidence │      │   Risk   │      │ Quality  │            │
│  │Calculator │      │ Assessor │      │Evaluator │            │
│  └─────┬────┘      └─────┬────┘      └─────┬────┘            │
│        └──────────────────┼──────────────────┘                 │
│                           ▼                                      │
│                    ┌──────────────┐                              │
│                    │ Coverage    │                              │
│                    │ Analyzer    │                              │
│                    └──────┬───────┘                              │
│                           ▼                                      │
│                    ┌──────────────┐                              │
│                    │ Ambiguity    │                              │
│                    │ Detector     │                              │
│                    └──────┬───────┘                              │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Output: ConfidenceScore (0-100%) + Factors + Recommendation │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## Dependencias

| Dependencia | Tipo | Descripción |
|-------------|------|-------------|
| EPIC 0 | Requerida | Foundation (Models) |
| EPIC 1 | Requerida | Knowledge Graph |
| EPIC 2 | Requerida | Reasoning Engine |
| EPIC 3 | Requerida | Evidence Retrieval |

---

## Estado del Proyecto

| EPIC | Estado |
|------|--------|
| EPIC 0 | ✅ COMPLETO |
| EPIC 1 | ✅ COMPLETO |
| EPIC 2 | ✅ COMPLETO |
| EPIC 3 | ✅ COMPLETO |
| EPIC 4 | ✅ COMPLETO |

---

## Referencias

- [ADR-3040: Confidence Engine Architecture](./adr/ADR-3040.md)
- [ADR-3041: Confidence Calculation Design](./adr/ADR-3041.md)
- [ADR-3042: Risk Assessment Design](./adr/ADR-3042.md)
- [ADR-3043: Uncertainty Quantification Design](./adr/ADR-3043.md)

---

*Document created: 2026-07-21*
*Last updated: 2026-07-21*
