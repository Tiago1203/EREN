# Vector Memory Plugin (VMP)

> **EREN's first REAL vector memory provider.** Provides vector storage for semantic search.

## Philosophy

The Kernel Cognitivo never knows:
- ChromaDB
- Qdrant
- Pinecone
- Milvus
- Weaviate
- pgvector

It only knows `BaseMemoryInterface`.

## Architecture

```
ExecutionCoordinator
        │
        ▼
Memory Engine
        │
        ▼
Memory Coordinator
        │
        ▼
Semantic Retrieval Engine
        │
        ▼
Vector Memory Plugin
        │
        ▼
ChromaDB (development)
        │
        ▼
Qdrant / pgvector / Pinecone (production)
```

## Complete Flow

```
Document
        │
        ▼
Chunker
        │
        ▼
Embedding Layer
        │
        ▼
Vector Memory Plugin
        │
        ▼
Semantic Retrieval Engine
        │
        ▼
LLM
```

## Features

- ✅ Store documents
- ✅ Store embeddings
- ✅ Semantic search
- ✅ Delete documents
- ✅ Update documents
- ✅ Filter by metadata
- ✅ Hybrid search
- ✅ Batch insert
- ✅ Batch search
- ✅ Multiple chunking strategies

## Chunking Strategies

| Strategy | Description |
|----------|-------------|
| `SentenceChunker` | Splits by sentence boundaries |
| `ParagraphChunker` | Splits by paragraphs |
| `SlidingWindowChunker` | Fixed-size sliding window |
| `RecursiveChunker` | Recursive hierarchical splitting |

## Usage

### Basic Usage

```python
from plugins.vector_memory import VectorMemoryPlugin, VectorMetadata

# Create plugin
plugin = VectorMemoryPlugin()
await plugin.initialize({
    "persist_directory": "./chroma_data",
    "collection_name": "eren_vectors",
    "embedding_model": "text-embedding-3-small",
})

# Add document
chunk_ids = await plugin.add_document(
    document_id="doc-123",
    content="This is a medical document about patient symptoms...",
    metadata=VectorMetadata(
        source="medical_report",
        author="Dr. Smith",
        medical_specialty="cardiology",
    ),
)

# Search
results = await plugin.search_similar(
    query="patient symptoms",
    top_k=5,
    min_score=0.7,
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Content: {result.content[:100]}...")
```

### With Memory Coordinator

```python
from core.memory import MemoryCoordinator
from plugins.vector_memory import VectorMemoryPlugin

# Create coordinator
coordinator = MemoryCoordinator()

# Create and register plugin
plugin = VectorMemoryPlugin()
await plugin.initialize({})
coordinator.registry.register(plugin.memory_provider)

# Write through coordinator
entry = MemoryEntry(
    content="Important medical information...",
    memory_type=MemoryType.VECTOR,
    metadata={"source": "medical_report"},
)
await coordinator.write(entry)

# Read through coordinator
result = await coordinator.read("medical information")
```

### Custom Chunker

```python
from plugins.vector_memory import (
    VectorMemoryPlugin,
    ParagraphChunker,
    RecursiveChunker,
)

# Use paragraph chunker
plugin = VectorMemoryPlugin(
    chunker=ParagraphChunker(max_chunk_size=1000, overlap=100),
)

# Or recursive chunker
plugin = VectorMemoryPlugin(
    chunker=RecursiveChunker(chunk_size=500),
)
```

### Batch Operations

```python
# Batch add documents
documents = [
    ("doc-1", "Content of document 1...", None),
    ("doc-2", "Content of document 2...", None),
    ("doc-3", "Content of document 3...", None),
]

chunk_ids_list = await plugin.batch_add_documents(documents)

# Batch search
queries = ["symptoms", "treatment", "diagnosis"]
results_list = await plugin.batch_search(queries)
```

## Metadata

Each chunk has the following metadata:

| Field | Description |
|-------|-------------|
| `document_id` | Parent document ID |
| `chunk_id` | Unique chunk identifier |
| `source` | Document source |
| `author` | Document author |
| `created_at` | Creation timestamp |
| `updated_at` | Update timestamp |
| `medical_specialty` | Medical specialty (if applicable) |
| `device` | Device identifier |
| `patient` | Patient identifier |
| `tags` | List of tags |
| `language` | Document language |
| `embedding_model` | Model used for embedding |
| `chunk_index` | Index in document |
| `total_chunks` | Total chunks in document |

## Providers

| Provider | Description | Status |
|----------|-------------|--------|
| `ChromaVectorProvider` | ChromaDB | ✅ Ready |
| `QdrantProvider` | Qdrant | 🔜 Future |
| `PgVectorProvider` | PostgreSQL | 🔜 Future |
| `PineconeProvider` | Pinecone | 🔜 Future |

## Integration

### With Retrieval Engine

```python
from core.retrieval import SemanticRetrievalEngine, MemorySource

# Create engine
engine = SemanticRetrievalEngine()

# Register vector memory
engine.register_memory_provider(
    MemorySource.VECTOR,
    plugin.memory_provider.read,
)

# Search through engine
context = engine.retrieve_text("What did the user ask?")
```

### With Embedding Layer

```python
from core.embeddings import EmbeddingManager

# Embeddings are generated automatically
# using the configured Embedding Manager
```

## Not Implemented Yet

- Reranking with AI
- Knowledge Graph integration
- Contextual compression
- Citation Engine

## Testing

```bash
pytest tests/unit/plugins/vector_memory/ -v
```

## License

EREN OS License
