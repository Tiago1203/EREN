# EPIC 4: Vector Indexing Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Indexar conocimiento biomédico.

---

## Responsabilidad

**Administrar el índice vectorial.**

EPIC 4 es responsable de:
- Gestionar colecciones en Qdrant
- Indexar vectores de embeddings
- Construir payloads estructurados
- Gestionar snapshots
- Monitorear estado del índice

---

## Dependencias

### EPICs
- **EPIC 3**: Consume EmbeddingVector de Clinical Embeddings

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                EPIC 4: Vector Indexing Engine                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     EmbeddingVector (de EPIC 3)                        │   │
│  │     Text chunks, entities, concepts                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       QDRANT                               │   │
│  │  ├── QdrantClientWrapper ───► Real Qdrant client         │   │
│  │  └── InMemoryQdrantClient ──► Testing client              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     COLLECTIONS                            │   │
│  │  ├── CollectionFactory ────► Create collections            │   │
│  │  ├── CollectionManager ────► Manage collections            │   │
│  │  └── CollectionStats ─────► Statistics                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       PAYLOADS                             │   │
│  │  ├── KnowledgePayloadBuilder ───► Knowledge payloads       │   │
│  │  ├── EntityPayloadBuilder ────► Entity payloads          │   │
│  │  └── PayloadSchema ──────────► Schema validation          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      INDEXER                               │   │
│  │  ├── VectorIndexer ─────────► Index vectors                │   │
│  │  └── VectorSearchEngine ────► Search vectors               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     Indexed vectors ready for retrieval                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic4_vector_indexing/
├── __init__.py                    # Módulo principal
├── qdrant/                        # Cliente Qdrant
│   └── __init__.py               # QdrantClient, configs
├── collections/                    # Gestión de colecciones
│   └── __init__.py               # CollectionManager, Factory
└── payloads/                      # Payload builders
    └── __init__.py               # PayloadBuilder, Schema
```

---

## Componentes

### 1. Qdrant

| Componente | Descripción |
|------------|-------------|
| `QdrantConfig` | Configuración de conexión |
| `InMemoryQdrantClient` | Cliente en memoria (testing) |
| `QdrantClientWrapper` | Wrapper para cliente real |

### 2. Collections

| Componente | Descripción |
|------------|-------------|
| `CollectionConfig` | Configuración de colección |
| `CollectionStats` | Estadísticas |
| `VectorCollection` | Modelo de colección |
| `CollectionFactory` | Fábrica de colecciones |
| `CollectionManager` | Gestión de colecciones |

### 3. Payloads

| Componente | Descripción |
|------------|-------------|
| `VectorPayload` | Payload de vector |
| `KnowledgePayloadBuilder` | Builder para conocimiento |
| `EntityPayloadBuilder` | Builder para entidades |
| `PayloadSchema` | Esquema de validación |

---

## Colecciones

### Tipos de Colección

```python
class CollectionType(str, Enum):
    KNOWLEDGE = "knowledge"   # Documentos y conocimiento
    DOCUMENTS = "documents"   # Documentos completos
    ENTITIES = "entities"     # Entidades biomédicas
    CONCEPTS = "concepts"     # Conceptos clínicos
    EMBEDDINGS = "embeddings" # Embeddings simples
```

### Templates de Colección

```python
# knowledge: Para documentos médicos
CollectionConfig(vector_size=384, distance="Cosine", m=16)

# entities: Para entidades biomédicas
CollectionConfig(vector_size=384, distance="Cosine", m=12)

# concepts: Para conceptos clínicos
CollectionConfig(vector_size=384, distance="Cosine", m=16)
```

---

## Uso

### Crear colección

```python
from core.PHASE_4.epic4_vector_indexing import (
    InMemoryQdrantClient,
    CollectionFactory,
    CollectionManager,
)

# Crear cliente
client = InMemoryQdrantClient()

# Crear colección
collection = CollectionFactory.create_knowledge_collection(
    name="medical_knowledge",
    vector_size=384,
)

# Crear en manager
manager = CollectionManager(client)
await manager.create_collection(collection)
```

### Indexar vectores

```python
from core.PHASE_4.epic4_vector_indexing import (
    VectorIndexer,
    KnowledgePayloadBuilder,
)

indexer = VectorIndexer(client)
builder = KnowledgePayloadBuilder()

# Construir payload
payload = builder.build({
    "source_id": "doc_123",
    "text": "Patient presents with chest pain...",
    "domain": "cardiology",
    "icd_codes": ["I25"],
})

# Indexar
await indexer.index(
    collection_name="medical_knowledge",
    vector=[0.1, 0.2, ...],  # 384 dims
    payload=payload.to_dict(),
)
```

### Buscar vectores

```python
from core.PHASE_4.epic4_vector_indexing import VectorSearchEngine

search = VectorSearchEngine(client)

results = await search.search(
    collection_name="medical_knowledge",
    query_vector=query_embedding,
    limit=10,
    score_threshold=0.7,
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Text: {result.payload['text'][:100]}")
```

---

## Payload Schema

```python
{
    "id": "keyword",
    "source_id": "keyword",
    "text": "text",
    "title": "text",
    "domain": "keyword",
    "source_type": "keyword",
    "icd_codes": ["keyword"],
    "snomed_codes": ["keyword"],
    "quality_score": "float",
    "confidence_score": "float",
    "created_at": "datetime",
}
```

---

## Concatenación

```
EPIC 3 ──► EPIC 4 (consume EmbeddingVector)
EPIC 0 ──► EPIC 4 (usa Foundation types)
EPIC 4 ──► EPIC 5 (provee IndexedVector para retrieval)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 5: Hybrid Retrieval Engine
- EPIC 6: Clinical RAG Pipeline

---

*EREN PHASE 4 - EPIC 4*
*Architecture Board - 2026-07-23*
