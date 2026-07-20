# EREN Epic 12 — RAG Pipeline

*Version 1.0 - 2026-07-20*

**Retrieval Augmentation Generation.**

Epic 12 implementa el RAG Pipeline — el sistema que recupera conocimiento relevante y lo integra con generación LLM.

---

## Purpose

El RAG Pipeline es responsable de:

- **Recuperar** documentos relevantes de múltiples fuentes
- **Reorganizar** resultados para máxima relevancia
- **Construir** prompts con contexto recuperado
- **Citar** fuentes en las respuestas

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       RAG PIPELINE                                  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Query      │  │  Retrieval  │  │     Reranker         │ │
│  │  Processing │──│  (Hybrid)   │──│     (Cross-encoder)   │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Context    │  │   Prompt    │  │    Citation          │ │
│  │  Builder    │──│   Builder   │──│    Builder           │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Query Processing
- Query expansion
- Query rewriting
- Query decomposition

### 2. Hybrid Retrieval
- Dense retrieval (embeddings)
- Sparse retrieval (BM25)
- Late interaction (ColBERT)

### 3. Reranker
- Cross-encoder reranking
- Learning-to-rank
- Diversity reranking

### 4. Context Builder
- Semantic chunking
- Context window management
- Token budget enforcement

### 5. Prompt Builder
- Template management
- Few-shot examples
- System prompt composition

### 6. Citation Builder
- Source attribution
- Citation formatting
- Verbatim quoting

---

## ADR Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-1200 | RAG Pipeline Architecture | Proposed |
| ADR-1201 | Retrieval Strategy | Proposed |
| ADR-1202 | Embedding Models | Proposed |
| ADR-1203 | Reranking Strategy | Proposed |
| ADR-1204 | Context Construction | Proposed |
| ADR-1205 | Citation Format | Proposed |

---

## Implementation Location

- `core/rag/` - Main RAG pipeline
- `core/embeddings/` - Embedding models
- `core/retrieval/` - Retrieval implementations

---

## Status

**Epic 12 Status:** PENDING

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status |
|------|--------|
| EPIC 11 (Reasoning Engine) | IN PROGRESS |
| **EPIC 12 (RAG Pipeline)** | 🚧 NEXT |
| EPIC 13 (Orchestrator) | PENDING |
| EPIC 14 (Agent Runtime) | PENDING |
| EPIC 15 (Memory & Learning) | PENDING |

---

*EREN Epic 12 v1.0 - RAG Pipeline*
*Architecture Board - 2026-07-20*
