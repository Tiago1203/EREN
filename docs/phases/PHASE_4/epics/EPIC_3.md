# EPIC 3: Clinical Embedding Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Generar embeddings clínicos optimizados.

---

## Responsabilidad

**Transformar conocimiento biomédico en vectores.**

EPIC 3 es responsable de:
- Generar embeddings de modelos biomédicos especializados
- Gestionar cache de embeddings
- Versionar embeddings
- Validar calidad de embeddings
- Optimizar procesamiento en batch

---

## Dependencias

### Fases
- **FASE 2**: Usa embeddings pipeline
- **FASE 3**: Integra con reasoning engine

### EPICs
- **EPIC 0**: Usa Foundation (tipos, eventos)
- **EPIC 2**: Consume ExtractedKnowledge

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│              EPIC 3: Clinical Embedding Engine                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     ExtractedKnowledge (de EPIC 2)                     │   │
│  │     Text (from any source)                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      PROVIDERS                            │   │
│  │  ├── MockEmbeddingProvider ─── Testing                    │   │
│  │  ├── SentenceTransformerProvider ── Local models         │   │
│  │  ├── OllamaProvider ─────────── Local LLM                  │   │
│  │  └── OpenAIProvider ─────────── Cloud API                  │   │
│  │                                                              │   │
│  │              EmbeddingProviderFactory                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        CACHE                               │   │
│  │  ├── InMemoryEmbeddingCache ──── LRU cache                │   │
│  │  └── PersistentEmbeddingCache ── JSON file cache          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      VERSIONING                           │   │
│  │  ├── InMemoryVersionManager ──── Version tracking         │   │
│  │  └── VersionComparator ───────── Similarity comparison    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      PIPELINES                            │   │
│  │  ├── EmbeddingPipeline ───────── Full pipeline            │   │
│  │  └── BatchGenerator ──────────── Batch processing         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     EmbeddingVector (biomédico, versionado, cacheado)     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic3_clinical_embeddings/
├── __init__.py                    # Módulo principal
├── providers/                      # Providers de embedding
│   └── __init__.py               # Mock, SentenceTransformer, Ollama, OpenAI
├── cache/                         # Cache de embeddings
│   └── __init__.py               # InMemory, Persistent cache
├── versioning/                    # Versionado
│   └── __init__.py               # VersionManager, Comparator
└── pipelines/                     # Pipelines
    └── __init__.py               # EmbeddingPipeline, BatchGenerator
```

---

## Componentes

### 1. Providers

| Provider | Descripción |
|----------|-------------|
| `MockEmbeddingProvider` | Para testing |
| `SentenceTransformerProvider` | Modelos locales |
| `OllamaProvider` | Modelos locales via Ollama |
| `OpenAIProvider` | OpenAI embeddings API |
| `EmbeddingProviderFactory` | Fábrica de providers |

### 2. Cache

| Cache | Descripción |
|-------|-------------|
| `InMemoryEmbeddingCache` | LRU cache en memoria |
| `PersistentEmbeddingCache` | Cache persistente en JSON |

### 3. Versioning

| Componente | Descripción |
|------------|-------------|
| `InMemoryVersionManager` | Gestión de versiones |
| `VersionComparator` | Comparación de versiones |

### 4. Pipelines

| Pipeline | Descripción |
|----------|-------------|
| `EmbeddingPipeline` | Pipeline completo |
| `BatchGenerator` | Generación en batch |

---

## Modelos de Embedding

```python
class EmbeddingModel(str):
    PUBMEDBERT = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    BIOBERT = "dmis-lab/biobert-base-cased-v1.2"
    CLINICALBERT = "emilyalsentzer/Bio_ClinicalBERT"
    SCIBERT = "allenai/scibert_scivocab_uncased"
    BLUEBERT = "bionlp/bluebert_pubmed_mimic_uncased"
```

---

## Uso

### Generación básica de embedding

```python
from core.PHASE_4.epic3_clinical_embeddings import (
    EmbeddingProviderFactory,
    InMemoryEmbeddingCache,
)

# Crear provider
provider = EmbeddingProviderFactory.create("mock", dimension=384)

# Crear cache
cache = InMemoryEmbeddingCache(max_size=1000)

# Generar embedding
embedding = await provider.generate("Patient with heart failure")
print(f"Vector dimension: {len(embedding.vector)}")
```

### Pipeline completo

```python
from core.PHASE_4.epic3_clinical_embeddings import (
    MockEmbeddingProvider,
    InMemoryEmbeddingCache,
    EmbeddingPipeline,
)

# Crear componentes
provider = MockEmbeddingProvider(dimension=384)
cache = InMemoryEmbeddingCache()
pipeline = EmbeddingPipeline(provider, cache=cache)

# Generar
result = await pipeline.generate("Clinical evidence about diabetes")
print(f"Vector: {result.vector[:5]}...")
print(f"Cached: {result.cached}")
```

### Batch processing

```python
from core.PHASE_4.epic3_clinical_embeddings import (
    MockEmbeddingProvider,
    EmbeddingPipeline,
    BatchGenerator,
)

provider = MockEmbeddingProvider()
pipeline = EmbeddingPipeline(provider)
batch_gen = BatchGenerator(pipeline, batch_size=32)

texts = ["Text 1", "Text 2", "Text 3", ...]
results = await batch_gen.generate(texts)

for result in results:
    print(f"Dimension: {result.dimension}")
```

---

## Flujo de Embedding

```
1. INPUT: ExtractedKnowledge o texto
          │
          ▼
2. HASH: Compute text hash
          │
          ▼
3. CACHE: Check InMemoryEmbeddingCache
          │
          ├── CACHE HIT ──► Return cached embedding
          │
          └── CACHE MISS ▼
4. PROVIDER: Generate embedding (Mock, Ollama, OpenAI, etc.)
          │
          ▼
5. VALIDATE: Validate embedding quality
          │
          ▼
6. VERSION: Create version (if version_manager)
          │
          ▼
7. CACHE: Store in cache
          │
          ▼
8. OUTPUT: EmbeddingVector (dimension, model, vector)
          │
          ▼
9. NEXT: EPIC 4 (Vector Indexing)
```

---

## Concatenación

```
EPIC 2 ──► EPIC 3 (consume ExtractedKnowledge)
EPIC 0 ──► EPIC 3 (usa Foundation types)
EPIC 3 ──► EPIC 4 (provee EmbeddingVector)
EPIC 3 ──► FASE 2 (provee para embeddings pipeline)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 4: Vector Indexing (Qdrant)
- EPIC 5: Hybrid Retrieval

---

*EREN PHASE 4 - EPIC 3*
*Architecture Board - 2026-07-23*
