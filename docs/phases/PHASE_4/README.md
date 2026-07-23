# EREN PHASE 4 — Knowledge Infrastructure

*Version 1.0 - 2026-07-23*

**La capa de infraestructura de conocimiento.**

FASE 4 implementa Knowledge Infrastructure — embeddings clínicos, integración Qdrant, recuperación de conocimiento, pipeline RAG clínico, y sistema de citación.

---

## Overview

FASE 4 conecta todas las capacidades anteriores:

- **PHASE_1**: Consume conocimiento del dominio (10 Bounded Contexts)
- **PHASE_2**: Extiende embeddings, retrieval, y RAG
- **PHASE_3**: Integra con motores de inteligencia clínica

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 4 — Knowledge Infrastructure               │
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────────┐ │
│  │  EMBEDDINGS  │ │   QDRANT    │ │         KNOWLEDGE           │ │
│  │   Clinical   │ │   Vector    │ │        Retrieval            │ │
│  │   Provider   │ │    Store     │ │                             │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────────┘ │
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────────┐ │
│  │     RAG      │ │  CITATIONS   │ │       INTEGRATION           │ │
│  │   Pipeline   │ │   Engine     │ │      (PHASE 2/3)            │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Módulos

### Embeddings

```
core/PHASE_4/embeddings/
├── __init__.py
├── medical_embedding.py    # Providers para embeddings biomédicos
├── clinical_chunker.py     # Chunking especializado
└── types.py               # Tipos y enums
```

### Qdrant

```
core/PHASE_4/qdrant/
├── __init__.py
├── client.py              # Cliente Qdrant
├── collection_manager.py   # Gestión de colecciones
├── vector_store.py        # Operaciones de vector store
└── hybrid_search.py       # Búsqueda híbrida
```

### Knowledge

```
core/PHASE_4/knowledge/
├── __init__.py
├── retriever.py           # Recuperador de conocimiento
├── evidence_searcher.py   # Buscador de evidencia
└── article_retriever.py   # Recuperador de artículos
```

### RAG

```
core/PHASE_4/rag/
├── __init__.py
├── clinical_pipeline.py   # Pipeline RAG clínico
├── orchestrator.py        # Orquestador
└── query_processor.py     # Procesador de queries
```

### Citations

```
core/PHASE_4/citations/
├── __init__.py
├── citation_builder.py    # Generador de citas
├── source_attributor.py   # Atribución de fuentes
└── evidence_tracer.py    # Trazabilidad de evidencia
```

---

## Dependencias

### PHASE_1 (Consume)

- Device Context
- Incident Context
- Knowledge Context
- Recommendation Context
- Asset Context
- Organization Context
- Inventory Context
- Department Context
- Staffing Context
- Capacity Context
- PostgreSQL
- UnitOfWork
- Domain Events

### PHASE_2 (Extiende)

- Context Builder
- Prompt Builder
- Provider Manager
- Memory Manager
- Embedding Services
- Retrieval Services
- RAG Services
- Runtime Integration

### PHASE_3 (Integra)

- Biomedical Knowledge Engine
- Reasoning Engine
- Medical Evidence Engine
- Confidence Engine
- Explainability Engine
- Safety Engine
- Clinical Validation Engine
- Decision Engine

---

## Quick Start

```python
from core.PHASE_4 import (
    MedicalEmbeddingProvider,
    QdrantClient,
    KnowledgeRetriever,
    ClinicalRAGPipeline,
    CitationBuilder,
)

# Initialize components
embedding_provider = MedicalEmbeddingProvider()
qdrant_client = QdrantClient(url="http://localhost:6333")
knowledge_retriever = KnowledgeRetriever(vector_store=qdrant_client)
citation_builder = CitationBuilder()

# Create RAG pipeline
pipeline = ClinicalRAGPipeline(
    knowledge_retriever=knowledge_retriever,
    citation_builder=citation_builder,
)

# Query
response = await pipeline.query(
    "What are the safety protocols for infusion pumps?"
)
```

---

## ADR Index

Ver `adr/README.md` para ADRs de arquitectura.

---

## EPICs

| EPIC | Nombre | Descripción |
|------|--------|-------------|
| EPIC 0 | Architecture Foundation | Estructura base, contracts, interfaces |
| EPIC 1 | Clinical Embeddings | Embeddings especializados para conocimiento biomédico |
| EPIC 2 | Qdrant Integration | Integración con vector DB |
| EPIC 3 | Knowledge Retriever | Recuperador específico para conocimiento clínico |
| EPIC 4 | RAG Orchestrator | Pipeline RAG clínico |
| EPIC 5 | Citation Engine | Generación de citas y atribución de fuentes |
| EPIC 6 | Integration | Integración con PHASE_2 y PHASE_3 |
| EPIC 7 | Testing & Validation | Tests y validación |
| EPIC 8 | Documentation | Documentación completa |

---

## Status

**PHASE 4 Status:** 🚧 IN PROGRESS

---

*EREN PHASE 4 v1.0*
*Architecture Board - 2026-07-23*
