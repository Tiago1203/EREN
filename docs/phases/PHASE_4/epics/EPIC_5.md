# EPIC 5: Hybrid Retrieval Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Recuperar el mejor conocimiento disponible.

---

## Responsabilidad

**Realizar búsqueda híbrida.**

EPIC 5 es responsable de:
- Búsqueda semántica (vectores)
- Búsqueda por keywords (BM25)
- Fusión de resultados
- Re-ranking
- Query expansion

---

## Dependencias

### EPICs
- **EPIC 4**: Consume IndexedVector de Vector Indexing

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│               EPIC 5: Hybrid Retrieval Engine                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     Query (natural language)                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      SEARCH                                  │   │
│  │  ├── VectorSearcher ──────► Semantic similarity            │   │
│  │  ├── KeywordSearcher ─────► Exact match                    │   │
│  │  └── SemanticSearcher ────► Combined                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                         BM25                                │   │
│  │  ├── BM25Classic ───────── Standard BM25                 │   │
│  │  ├── BM25L ──────────────── For short docs               │   │
│  │  └── BM25Plus ───────────── Variant                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        FUSION                               │   │
│  │  ├── ReciprocalRankFusion ──► RRF (k=60)                 │   │
│  │  ├── WeightedAverage ────────► Weighted scores             │   │
│  │  ├── CombSUM ───────────────► Sum of scores              │   │
│  │  └── CombMNZ ───────────────► Sum × count                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     Ranked RetrievalResult (knowledge retrieved)          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic5_hybrid_retrieval/
├── __init__.py                    # Módulo principal
├── search/                        # Búsqueda
│   └── __init__.py              # VectorSearcher, KeywordSearcher, SemanticSearcher
├── bm25/                          # BM25
│   └── __init__.py              # BM25Classic, BM25L, BM25Plus
└── fusion/                        # Fusión
    └── __init__.py              # RRF, WeightedAverage, CombSUM, CombMNZ
```

---

## Componentes

### 1. Search

| Componente | Descripción |
|------------|-------------|
| `VectorSearcher` | Búsqueda semántica con embeddings |
| `KeywordSearcher` | Búsqueda por keywords |
| `SemanticSearcher` | Combinación de vector + keyword |

### 2. BM25

| Variante | Descripción |
|----------|-------------|
| `BM25Classic` | BM25 estándar (k1=1.5, b=0.75) |
| `BM25L` | Para documentos cortos |
| `BM25Plus` | Evita score zero |

### 3. Fusion

| Método | Descripción |
|--------|-------------|
| `ReciprocalRankFusion` | RRF: Σ 1/(k+rank) |
| `WeightedAverageFusion` | Promedio ponderado |
| `CombSUMFusion` | Suma de scores normalizados |
| `CombMNZFusion` | CombSUM × count |

---

## Uso

### Búsqueda híbrida básica

```python
from core.PHASE_4.epic5_hybrid_retrieval import (
    VectorSearcher,
    KeywordSearcher,
    SemanticSearcher,
    ReciprocalRankFusion,
)

# Crear searchers
vector_searcher = VectorSearcher()
keyword_searcher = KeywordSearcher()
semantic_searcher = SemanticSearcher(
    vector_searcher=vector_searcher,
    keyword_searcher=keyword_searcher,
)

# Búsqueda
response = await semantic_searcher.search(
    SearchParams(query="heart failure treatment", limit=10)
)
```

### BM25

```python
from core.PHASE_4.epic5_hybrid_retrieval import BM25Classic, BM25Searcher

# Crear index
bm25 = BM25Searcher(variant="classic")
documents = [
    {"id": "1", "text": "Heart failure is a common condition..."},
    {"id": "2", "text": "Diabetes management requires..."},
]
bm25.index_documents(documents)

# Buscar
results = bm25.search("heart failure", limit=10)
```

### Fusión RRF

```python
from core.PHASE_4.epic5_hybrid_retrieval import (
    FusionResult,
    ReciprocalRankFusion,
)

# Resultados de múltiples fuentes
vector_results = [
    FusionResult(doc_id="1", fused_score=0.9, source="vector"),
    FusionResult(doc_id="2", fused_score=0.8, source="vector"),
]
keyword_results = [
    FusionResult(doc_id="1", fused_score=0.7, source="keyword"),
    FusionResult(doc_id="3", fused_score=0.85, source="keyword"),
]

# Fusionar
rrf = ReciprocalRankFusion(k=60)
fused = rrf.fuse([vector_results, keyword_results])
```

---

## Flujo de Retrieval

```
1. INPUT: Query (natural language)
          │
          ▼
2. SEARCH: VectorSearcher + KeywordSearcher
          │
          ▼
3. BM25: Score con BM25Classic
          │
          ▼
4. FUSION: Combine con RRF o WeightedAverage
          │
          ▼
5. OUTPUT: Ranked RetrievalResult
          │
          ▼
6. NEXT: EPIC 6 (Clinical RAG Pipeline)
```

---

## Concatenación

```
EPIC 4 ──► EPIC 5 (consume IndexedVector)
EPIC 0 ──► EPIC 5 (usa Foundation types)
EPIC 5 ──► EPIC 6 (provee RetrievalResult)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 6: Clinical RAG Pipeline
- EPIC 7: Citation & Traceability

---

*EREN PHASE 4 - EPIC 5*
*Architecture Board - 2026-07-23*
