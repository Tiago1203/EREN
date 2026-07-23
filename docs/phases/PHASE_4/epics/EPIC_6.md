# EPIC 6: Clinical RAG Pipeline

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Construir el pipeline completo de Retrieval Augmented Generation.

---

## Responsabilidad

**Conectar Retrieval con la Inteligencia Clínica.**

EPIC 6 es responsable de:
- Procesar queries clínicas
- Construir contexto clínico
- Generar Prompt Context
- Crear Evidence Packages
- Optimizar contexto para prompts

---

## Dependencias

### Fases
- **FASE 2**: Integra con AI Core
- **FASE 3**: Conecta con Clinical Intelligence

### EPICs
- **EPIC 5**: Consume RetrievalResult de Hybrid Retrieval

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│               EPIC 6: Clinical RAG Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     Query (clinical question)                          │   │
│  │     RetrievalResult (from EPIC 5)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       QUERY                                  │   │
│  │  ├── ClinicalQueryProcessor ───► Classify intent           │   │
│  │  ├── QueryIntent ───────────────► Intent detection          │   │
│  │  └── ProcessedQuery ───────────► Normalized query          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       CONTEXT                              │   │
│  │  ├── ClinicalContextBuilder ────► Build context             │   │
│  │  ├── ContextOptimizer ──────────► Optimize tokens           │   │
│  │  └── PromptContextGenerator ────► Generate prompt           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       EVIDENCE                               │   │
│  │  ├── ClinicalEvidenceBuilder ───► Build evidence            │   │
│  │  ├── EvidenceItem ──────────────► Evidence item             │   │
│  │  └── EvidencePackage ───────────► Complete package          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     ClinicalContext + EvidencePackage + Prompt            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic6_clinical_rag/
├── __init__.py                    # Módulo principal
├── query/                         # Procesamiento de queries
│   └── __init__.py              # ClinicalQueryProcessor, etc.
├── context/                       # Construcción de contexto
│   └── __init__.py              # ClinicalContextBuilder, etc.
└── evidence/                      # Empaquetado de evidencia
    └── __init__.py              # ClinicalEvidenceBuilder, etc.
```

---

## Componentes

### 1. Query

| Componente | Descripción |
|------------|-------------|
| `ClinicalQueryProcessor` | Procesa y clasifica queries |
| `QueryIntent` | Intención detectada |
| `ProcessedQuery` | Query procesada |

**Tipos de Query:**
- `DIAGNOSIS` - Diagnóstico diferencial
- `TREATMENT` - Recomendación de tratamiento
- `DEVICE_USAGE` - Uso de dispositivos
- `TROUBLESHOOTING` - Resolución de problemas
- `SAFETY_ALERT` - Alertas de seguridad
- `REGULATORY` - Cumplimiento regulatorio

### 2. Context

| Componente | Descripción |
|------------|-------------|
| `ClinicalContext` | Contexto clínico |
| `ClinicalContextBuilder` | Builder de contexto |
| `ContextOptimizer` | Optimiza tokens |
| `PromptContextGenerator` | Genera prompts |

### 3. Evidence

| Componente | Descripción |
|------------|-------------|
| `EvidencePackage` | Paquete de evidencia |
| `EvidenceItem` | Item de evidencia |
| `ClinicalEvidenceBuilder` | Builder de evidencia |
| `EvidenceQuality` | Calidad (HIGH, MEDIUM, LOW) |
| `EvidenceType` | Tipo (peer_reviewed, guideline, etc.) |

---

## Uso

### Procesamiento de Query

```python
from core.PHASE_4.epic6_clinical_rag import ClinicalQueryProcessor

processor = ClinicalQueryProcessor()
query = processor.process("What is the treatment for heart failure?")

print(f"Type: {query.intent.query_type}")
print(f"Confidence: {query.intent.confidence}")
print(f"Terms: {query.intent.medical_terms}")
```

### Construcción de Contexto

```python
from core.PHASE_4.epic6_clinical_rag import ClinicalContextBuilder

builder = ClinicalContextBuilder()
context = builder.build(
    query="Treatment for heart failure",
    retrieved_chunks=[
        {"id": "1", "text": "ACE inhibitors are recommended...", "score": 0.9},
        {"id": "2", "text": "Beta blockers help...", "score": 0.8},
    ]
)

print(context.to_prompt_text())
```

### Construcción de Evidence Package

```python
from core.PHASE_4.epic6_clinical_rag import ClinicalEvidenceBuilder

builder = ClinicalEvidenceBuilder()
evidence = builder.build(
    query="Heart failure treatment",
    retrieved_chunks=[...]
)

print(f"Total evidence: {evidence.total_evidence}")
print(f"High quality: {evidence.high_quality_count}")
print(f"Citations: {evidence.get_citations()}")
```

---

## Flujo de RAG

```
1. INPUT: Query + RetrievalResult (from EPIC 5)
          │
          ▼
2. QUERY: ClinicalQueryProcessor
          │ Query → ProcessedQuery
          │ Intent classification
          │
          ▼
3. CONTEXT: ClinicalContextBuilder
          │ Chunks → ClinicalContext
          │ Relevance filtering
          │
          ▼
4. EVIDENCE: ClinicalEvidenceBuilder
          │ Chunks → EvidencePackage
          │ Quality assessment
          │
          ▼
5. OPTIMIZE: ContextOptimizer
          │ Token optimization
          │
          ▼
6. GENERATE: PromptContextGenerator
          │ ClinicalContext → Prompt
          │
          ▼
7. OUTPUT: PromptContext (ready for LLM)
          │
          ▼
8. NEXT: PHASE 3 (Clinical Intelligence) / LLM
```

---

## Concatenación

```
EPIC 5 ──► EPIC 6 (consume RetrievalResult)
EPIC 0 ──► EPIC 6 (usa Foundation types)
FASE 2 ──► EPIC 6 (usa Context Builder)
FASE 3 ──► EPIC 6 (conecta con Intelligence)
EPIC 6 ──► EPIC 7 (provee EvidencePackage para citaciones)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 7: Citation & Traceability Engine
- EPIC 8: Knowledge Quality Engine

---

*EREN PHASE 4 - EPIC 6*
*Architecture Board - 2026-07-23*
