# EPIC 5: Explainability Engine

**Estado:** ✅ COMPLETO
**Fecha de inicio:** 2026-07-21
**Epic Owner:** Architecture Team
**Depende de:** EPIC 2 (Reasoning Engine), EPIC 3 (Evidence Retrieval), EPIC 4 (Confidence Engine)

---

## Objetivo

Construir el motor de explicabilidad que convierte las recomendaciones de EREN en lenguaje humano comprensible. El Explainability Engine responde a la pregunta fundamental:

> **"¿Por qué EREN recomienda esto?"**

Este módulo es crítico porque:
- Proporciona transparencia en las decisiones de EREN
- Permite a los profesionales de salud validar las recomendaciones
- Genera documentación auditable para compliance
- Construye confianza en el sistema

---

## Filosofía

El Explainability Engine implementa un principio fundamental de EREN:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   Si EREN responde "Cambie el sensor."                                        │
│                                                                              │
│   DEBE explicar POR QUÉ:                                                     │
│                                                                              │
│   "Cambie el sensor porque:                                                  │
│    - El modo de fallo 12 indica degradación del sensor                      │
│    - 3 incidentes similares ocurrieron en los últimos 6 meses                 │
│    - El boletín del fabricante menciona este problema                        │
│    - IEC 60601-2-61 requiere calibración < 180 días (han pasado 210)        │
│    - El historial muestra voltaje fuera de rango                              │
│                                                                              │
│    Confianza: 93%"                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXPLAINABILITY ENGINE (EPIC 5)                             │
│                                                                              │
│  INPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ From Reasoning + Evidence + Confidence (EPIC 2 + 3 + 4)               │    │
│  │ ├── Recommendation                                                     │    │
│  │ ├── Reasoning Chains                                                    │    │
│  │ ├── Evidence Bundle                                                    │    │
│  │ └── Confidence Score                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EXPLAINABILITY COMPONENTS                           │    │
│  │                                                                       │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │    │
│  │   │ Reasoning   │  │  Evidence   │  │  Decision   │                │    │
│  │   │   Graph     │  │   Tree      │  │    Path     │                │    │
│  │   │  Generator  │  │   Builder   │  │   Tracer    │                │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                │    │
│  │          │               │               │                            │    │
│  │          └───────────────┼───────────────┘                            │    │
│  │                          │                                             │    │
│  │   ┌─────────────┐  ┌─────────────┐                                  │    │
│  │   │  Source    │  │  Natural    │                                  │    │
│  │   │  Tracer    │  │  Language   │                                  │    │
│  │   │            │  │  Explainer  │                                  │    │
│  │   └─────────────┘  └─────────────┘                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  OUTPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Explanation                                                           │    │
│  │ ├── Reasoning Graph (visual)                                           │    │
│  │ ├── Evidence Tree (justification)                                      │    │
│  │ ├── Decision Path (logic trace)                                        │    │
│  │ ├── Source Trace (citations)                                           │    │
│  │ └── Natural Language (human readable)                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. Reasoning Graph Generator

```
ReasoningGraphGenerator
├── GraphBuilder
│   ├── Node creation
│   ├── Edge creation
│   └── Layout calculation
├── GraphVisualizer
│   ├── DOT export
│   ├── SVG generation
│   └── Interactive viewer
└── GraphAnalyzer
    ├── Path finding
    ├── Critical path
    └── Influence analysis
```

**Responsabilidades:**
- Generar grafos visuales del razonamiento
- Mostrar relaciones entre conceptos
- Identificar caminos críticos

### 2. Evidence Tree Builder

```
EvidenceTreeBuilder
├── TreeConstructor
│   ├── Root node (recommendation)
│   ├── Branch nodes (evidence categories)
│   └── Leaf nodes (individual evidence)
├── TreeAnnotator
│   ├── Confidence annotation
│   ├── Source annotation
│   └── Relevance annotation
└── TreeExporter
    ├── JSON export
    ├── Markdown export
    └── HTML export
```

**Responsabilidades:**
- Construir árboles de evidencia jerárquicos
- Anotar con confianza y fuentes
- Exportar en múltiples formatos

### 3. Decision Path Tracer

```
DecisionPathTracer
├── PathExtractor
│   ├── From reasoning chains
│   ├── From rule matches
│   └── From hypothesis evaluation
├── PathAnalyzer
│   ├── Step-by-step analysis
│   ├── Branch identification
│   └── Alternative paths
└── PathVisualizer
    ├── Flowchart format
    └── Timeline format
```

**Responsabilidades:**
- Extraer paths de decisión
- Mostrar lógica paso a paso
- Identificar alternativas

### 4. Source Tracer

```
SourceTracer
├── CitationBuilder
│   ├── Standard citations
│   ├── Manufacturer references
│   └── Historical incidents
├── ProvenanceTracker
│   ├── Evidence provenance
│   ├── Knowledge provenance
│   └── Reasoning provenance
└── CitationFormatter
    ├── IEEE format
    ├── APA format
    └── Custom format
```

**Responsabilidades:**
- Rastrear fuentes de cada elemento
- Generar citaciones proper
- Mantener trazabilidad completa

### 5. Natural Language Explainer

```
NaturalLanguageExplainer
├── ExplanationGenerator
│   ├── Summary generator
│   ├── Detailed generator
│   └── Contrastive generator
├── LanguageTuner
│   ├── Clinical vocabulary
│   ├── Technical vocabulary
│   └── Layperson vocabulary
└── ExplanationFormatter
    ├── Structured text
    ├── Bullet points
    └── Narrative format
```

**Responsabilidades:**
- Generar explicaciones en lenguaje natural
- Adaptar vocabulario al audience
- Formatear para diferentes contextos

---

## Ejemplo: SpO2 Monitor

### Input

```
Recommendation: Replace sensor
Reasoning Chain: symptom → evidence → hypothesis → action
Evidence: Failure Mode 12, 3 incidents, Manufacturer bulletin, IEC
Confidence: 93%
```

### Output - Natural Language

```
EREN recommends: REPLACE SENSOR

Why?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The sensor should be replaced because:

1. FAILURE MODE 12 (Weight: 0.85)
   Evidence shows this device exhibits Failure Mode 12, 
   which indicates sensor degradation. This failure mode 
   accounts for 73% of similar incidents.

2. SIMILAR INCIDENTS (Weight: 0.80)
   3 incidents with identical symptoms occurred in the 
   past 6 months. All were resolved by sensor replacement.

3. MANUFACTURER BULLETIN (Weight: 0.90)
   GE Healthcare Bulletin SB-2024-05 specifically addresses 
   this issue and recommends sensor replacement.

4. IEC 60601-2-61 NON-COMPLIANCE (Weight: 0.75)
   Last calibration was 210 days ago. Standard requires 
   calibration < 180 days. This indicates degraded performance.

5. VOLTAGE ANOMALY (Weight: 0.70)
   Maintenance log shows voltage readings 15% outside normal 
   range for the past 30 days.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confidence: 93% (HIGH)

Supporting factors:
✓ Strong evidence from authoritative sources
✓ Multiple independent sources confirm
✓ Consistent with manufacturer guidance

Sources:
• GE Healthcare SpO2 Service Manual, p.42
• IEC 60601-2-61:2017 Clause 6.8.3
• Incident Database: #2024-00123, #2024-00145, #2024-00189

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Arquitectura de Archivos

```
core/
└── intelligence/
    └── explainability/                        # EPIC 5: Explainability Engine
        ├── __init__.py
        │
        ├── graphs/                          # Reasoning Graph Generator
        │   ├── __init__.py
        │   ├── reasoning_graph.py
        │   ├── graph_builder.py
        │   └── graph_visualizer.py
        │
        ├── trees/                           # Evidence Tree Builder
        │   ├── __init__.py
        │   ├── evidence_tree.py
        │   ├── tree_builder.py
        │   └── tree_exporter.py
        │
        ├── paths/                           # Decision Path Tracer
        │   ├── __init__.py
        │   ├── decision_path.py
        │   ├── path_extractor.py
        │   └── path_visualizer.py
        │
        ├── tracing/                        # Source Tracer
        │   ├── __init__.py
        │   ├── source_tracer.py
        │   ├── citation_builder.py
        │   └── provenance_tracker.py
        │
        ├── natural/                        # Natural Language Explainer
        │   ├── __init__.py
        │   ├── explanation_generator.py
        │   ├── language_tuner.py
        │   └── formatter.py
        │
        └── models/                        # Shared Models
            ├── __init__.py
            ├── explanation.py
            └── trace.py
```

---

## Dependencias

| Dependencia | Tipo | Descripción |
|-------------|------|-------------|
| EPIC 0 | Requerida | Foundation (Models) |
| EPIC 1 | Requerida | Knowledge Graph |
| EPIC 2 | Requerida | Reasoning Engine |
| EPIC 3 | Requerida | Evidence Retrieval |
| EPIC 4 | Requerida | Confidence Engine |

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

---

## Referencias

- [ADR-3050: Explainability Architecture](./adr/ADR-3050.md)
- [ADR-3051: Reasoning Graph Design](./adr/ADR-3051.md)
- [ADR-3052: Evidence Tree Design](./adr/ADR-3052.md)
- [ADR-3053: Natural Language Generation](./adr/ADR-3053.md)

---

*Document created: 2026-07-21*
*Last updated: 2026-07-21*
