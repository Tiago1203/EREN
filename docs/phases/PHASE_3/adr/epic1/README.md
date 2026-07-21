# EPIC 1: Biomedical Knowledge Engine - ADR Index

*Architecture Decision Records para EPIC 1*

---

## Tabla de ADRs

| ADR | Título | Estado | Severidad |
|-----|--------|--------|-----------|
| ADR-3010 | Knowledge Graph Architecture | 🚧 In Progress | Crítica |
| ADR-3011 | Medical Ontology Design | 🚧 In Progress | Alta |
| ADR-3012 | Equipment Taxonomy Design | 🚧 In Progress | Alta |
| ADR-3013 | Standards Repository Design | 🚧 In Progress | Alta |
| ADR-3014 | Evidence Store Architecture | 🚧 In Progress | Crítica |

**Total: 5 ADRs (0 Complete, 5 In Progress)**

---

## Resumen de Decisiones

### ADR-3010: Knowledge Graph
Arquitectura de grafo de conocimiento biomédico con nodos y aristas.

### ADR-3011: Medical Ontology
Integración de SNOMED-CT, ICD-10/11, LOINC con navegación jerárquica.

### ADR-3012: Equipment Taxonomy
Taxonomía de equipos médicos con modos de falla y lógica de mantenimiento.

### ADR-3013: Standards Repository
Repositorio de estándares IEC, ISO, AAMI, NFPA, FDA.

### ADR-3014: Evidence Store
Almacén de evidencia con múltiples fuentes (literatura, estándares, regulatorio).

---

## Ubicación de Archivos

```
docs/phases/PHASE_3/adr/epic1/
├── README.md
├── ADR-3010.md  (Knowledge Graph Architecture)
├── ADR-3011.md  (Medical Ontology Design)
├── ADR-3012.md  (Equipment Taxonomy Design)
├── ADR-3013.md  (Standards Repository Design)
└── ADR-3014.md  (Evidence Store Architecture)
```

---

## Conexión con EPIC 0

```
EPIC 0: Foundation ✅
        │
        ├── DTOs (ClinicalFinding, DiagnosisCandidate)
        ├── Contracts (IClinicalReasoner)
        ├── Models (Evidence, Safety)
        │
        ▼
EPIC 1: Biomedical Knowledge Engine 🚧
        │
        ├── Knowledge Graph
        ├── Medical Ontology
        ├── Equipment Taxonomy
        ├── Standards Repository
        └── Evidence Store
```

---

*EREN PHASE 3 ADR Index - EPIC 1*
*Architecture Board - 2026-07-21*
