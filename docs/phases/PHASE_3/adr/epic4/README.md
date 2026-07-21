# EPIC 4: Confidence Engine - ADR Index

*Architecture Decision Records para EPIC 4*

---

## Tabla de ADRs

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-3040 | Confidence Engine Architecture | ✅ COMPLETO |
| ADR-3041 | Confidence Calculation Design | ✅ COMPLETO |
| ADR-3042 | Risk Assessment Design | ✅ COMPLETO |
| ADR-3043 | Uncertainty Quantification Design | ✅ COMPLETO |

**Total: 4 ADRs (4 Complete)**

---

## Resumen de Decisiones

### ADR-3040: Confidence Engine Architecture
Arquitectura del motor de confianza con sus 5 componentes principales.

### ADR-3041: Confidence Calculation Design
Diseño del cálculo de confianza con Evidence, Knowledge, y Reasoning calculators.

### ADR-3042: Risk Assessment Design
Diseño de evaluación de riesgos con matriz de riesgos y niveles.

### ADR-3043: Uncertainty Quantification Design
Diseño de cuantificación de incertidumbre con tipos y factores.

---

## Ubicación de Archivos

```
docs/phases/PHASE_3/adr/epic4/
├── README.md
├── ADR-3040.md  (Confidence Engine Architecture)
├── ADR-3041.md  (Confidence Calculation Design)
├── ADR-3042.md  (Risk Assessment Design)
└── ADR-3043.md  (Uncertainty Quantification Design)
```

---

## Conexión con EPICs Anteriores

```
EPIC 0: Foundation ✅
        │
        └── Models (Confidence, Risk)

EPIC 1: Biomedical Knowledge Engine ✅
        │
        └── Knowledge Graph

EPIC 2: Reasoning Engine ✅
        │
        ├── Hypotheses
        ├── Reasoning Chains
        └── Diagnostics

EPIC 3: Evidence Retrieval ✅
        │
        ├── Evidence Bundle
        ├── Evidence Scoring
        └── Rules Engine

EPIC 4: Confidence Engine ✅ ← ESTE EPIC
        │
        ├── Confidence Calculator
        ├── Risk Assessor
        ├── Quality Evaluator
        ├── Coverage Analyzer
        └── Ambiguity Detector

EPIC 5: Explainability Engine ← NEXT
```

---

*EREN PHASE 3 ADR Index - EPIC 4*
*Architecture Board - 2026-07-21*
