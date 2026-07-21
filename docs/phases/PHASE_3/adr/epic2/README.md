# EPIC 2: Reasoning Engine - ADR Index

*Architecture Decision Records para EPIC 2*

---

## Tabla de ADRs

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-3020 | Reasoning Engine Architecture | ✅ COMPLETO |
| ADR-3021 | Hypothesis Engine Design | ✅ COMPLETO |
| ADR-3022 | Inference Engine Design | ✅ COMPLETO |
| ADR-3023 | Diagnostic Engine Design | ✅ COMPLETO |
| ADR-3024 | Causal Graph Design | ✅ COMPLETO |

**Total: 5 ADRs (5 Complete)**

---

## Resumen de Decisiones

### ADR-3020: Reasoning Engine Architecture
Arquitectura general del motor de razonamiento con pipeline de 7 stages.

### ADR-3021: Hypothesis Engine Design
Motor de generación y evaluación de hipótesis con actualización bayesiana.

### ADR-3022: Inference Engine Design
Motor de inferencia con forward/backward chaining y razonamiento abductivo.

### ADR-3023: Diagnostic Engine Design
Motor de diagnóstico con análisis diferencial y causa raíz.

### ADR-3024: Causal Graph Design
Grafo causal para representación y análisis de relaciones causales.

---

## Ubicación de Archivos

```
docs/phases/PHASE_3/adr/epic2/
├── README.md
├── ADR-3020.md  (Reasoning Engine Architecture)
├── ADR-3021.md  (Hypothesis Engine Design)
├── ADR-3022.md  (Inference Engine Design)
├── ADR-3023.md  (Diagnostic Engine Design)
└── ADR-3024.md  (Causal Graph Design)
```

---

## Conexión con EPIC 0 y EPIC 1

```
EPIC 0: Foundation ✅
        │
        ├── DTOs (ClinicalFinding, DiagnosisCandidate)
        ├── Contracts (IClinicalReasoner)
        └── Models (Evidence, Safety)

EPIC 1: Biomedical Knowledge Engine ✅
        │
        ├── Knowledge Graph
        ├── Medical Ontology
        ├── Equipment Taxonomy
        └── Evidence Store

EPIC 2: Reasoning Engine ✅ ← ESTE EPIC
        │
        ├── Hypothesis Engine
        ├── Inference Engine
        ├── Diagnostic Engine
        ├── Reasoning Chains
        └── Causal Graph
```

---

*EREN PHASE 3 ADR Index - EPIC 2*
*Architecture Board - 2026-07-21*
