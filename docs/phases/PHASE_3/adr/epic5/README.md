# EPIC 5: Explainability Engine - ADR Index

*Architecture Decision Records para EPIC 5*

---

## Tabla de ADRs

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-3050 | Explainability Architecture | ✅ COMPLETO |
| ADR-3051 | Reasoning Graph Design | ✅ COMPLETO |
| ADR-3052 | Evidence Tree Design | ✅ COMPLETO |
| ADR-3053 | Natural Language Generation | ✅ COMPLETO |

**Total: 4 ADRs (4 Complete)**

---

## Resumen de Decisiones

### ADR-3050: Explainability Architecture
Arquitectura del motor de explicabilidad con 5 componentes principales.

### ADR-3051: Reasoning Graph Design
Diseño del grafo de razonamiento con nodos y aristas.

### ADR-3052: Evidence Tree Design
Diseño del árbol de evidencia con categorización y anotaciones.

### ADR-3053: Natural Language Generation
Diseño de generación de lenguaje natural adaptable al audience.

---

## Ubicación de Archivos

```
docs/phases/PHASE_3/adr/epic5/
├── README.md
├── ADR-3050.md  (Explainability Architecture)
├── ADR-3051.md  (Reasoning Graph Design)
├── ADR-3052.md  (Evidence Tree Design)
└── ADR-3053.md  (Natural Language Generation)
```

---

## Conexión con EPICs Anteriores

```
EPIC 0: Foundation ✅
        │
        └── Models

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
        └── Rules Engine

EPIC 4: Confidence Engine ✅
        │
        └── Confidence Scores

EPIC 5: Explainability Engine ✅ ← ESTE EPIC
        │
        ├── Reasoning Graph
        ├── Evidence Tree
        ├── Decision Path
        ├── Source Trace
        └── Natural Language

EPIC 6: Biomedical Rules Engine ← NEXT
```

---

*EREN PHASE 3 ADR Index - EPIC 5*
*Architecture Board - 2026-07-21*
