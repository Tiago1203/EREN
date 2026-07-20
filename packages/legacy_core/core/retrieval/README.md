# Semantic Retrieval Engine (SRE)

> **EREN's Semantic Retrieval Engine.** The beginning of EREN's RAG system.

This component is responsible for retrieving relevant knowledge from multiple memory systems.

## Philosophy

The Retrieval Engine never knows:
- PostgreSQL
- SQLite
- Chroma
- Qdrant
- Pinecone
- FAISS
- Milvus
- Redis

It only knows contracts.

## Responsibilities

The engine is responsible only for deciding:
- **What to search**
- **Where to search**
- **How to combine results**
- **How to rank results**
- **How much context to return**
- **What information to discard**

## Architecture

```
ExecutionCoordinator
        │
        ▼
MemoryEngine
        │
        ▼
MemoryCoordinator
        │
        ▼
Semantic Retrieval Engine
        │
        ▼
Retrieval Planner
        │
        ▼
Retrieval Strategy
        │
        ▼
Result Ranker
        │
        ▼
Context Builder
        │
        ▼
Memory Providers (Contracts)
        │
   ┌────┼────┬─────────┐
   ▼    ▼    ▼         ▼
Conv  Sem  Clin  Device
Mem   Mem  Mem   Mem
```

## Components

| Component | Description |
|-----------|-------------|
| `engine.py` | Main retrieval engine |
| `planner.py` | Plans retrieval operations |
| `strategy.py` | Execution strategies |
| `ranker.py` | Ranks results |
| `context_builder.py` | Builds context for LLM |
| `registry.py` | Manages providers |
| `policies.py` | Retrieval policies |

## Usage

### Basic Usage

```python
from core.retrieval import SemanticRetrievalEngine, RetrievalQuery, MemorySource

# Create engine
engine = SemanticRetrievalEngine()

# Register memory providers
engine.register_memory_provider(
    MemorySource.CONVERSATION,
    conversation_memory_provider
)
engine.register_memory_provider(
    MemorySource.SEMANTIC,
    semantic_memory_provider
)

# Retrieve
query = RetrievalQuery(
    query="What did the user ask about patients?",
    sources=[MemorySource.CONVERSATION, MemorySource.SEMANTIC],
    max_results=5,
)
response = engine.retrieve(query)

print(response.content)
```

### Convenience Methods

```python
# Retrieve as text
context = engine.retrieve_text(
    query="What is the patient history?",
    sources=[MemorySource.CLINICAL, MemorySource.CONVERSATION],
)

# Retrieve with full response
context, response = engine.retrieve_with_context(
    query="What was discussed about diabetes?",
    max_context_tokens=2000,
)
```

## Policies

| Policy | Description |
|--------|-------------|
| `FASTEST` | Prioritize speed |
| `BEST_MATCH` | Prioritize relevance |
| `MERGE_ALL` | Merge all sources |
| `VECTOR_FIRST` | Query vector first |
| `SEMANTIC_FIRST` | Query semantic first |
| `HYBRID` | Combine vector and semantic |
| `CLINICAL_PRIORITY` | Prioritize clinical |
| `DEVICE_PRIORITY` | Prioritize device data |

## Memory Sources

| Source | Description |
|--------|-------------|
| `CONVERSATION` | Conversation history |
| `SEMANTIC` | Semantic knowledge |
| `CLINICAL` | Medical information |
| `DEVICE` | Device metrics |
| `VECTOR` | Vector embeddings |
| `WORKING` | Short-term memory |
| `LONG_TERM` | Persistent memory |

## Integration

### With Memory Coordinator

```python
from core.memory import MemoryCoordinator
from core.retrieval import SemanticRetrievalEngine

coordinator = MemoryCoordinator()

# Register all memories with retrieval engine
for memory in coordinator.registry.list_all():
    engine.register_memory_provider(
        memory.memory_type,
        memory.read
    )
```

### With Execution Coordinator

```python
from core.execution import ExecutionCoordinator
from core.retrieval import SemanticRetrievalEngine

coordinator = ExecutionCoordinator()
engine = SemanticRetrievalEngine()

# Coordinator uses engine for context retrieval
context = engine.retrieve_text("What is the current session about?")
```

## Not Implemented Yet

The following are NOT implemented in this PR:
- Embeddings generation
- Vector DB integration
- AI reranking
- Automatic chunking
- Contextual compression

These will come in future PRs.

## Testing

```bash
pytest tests/unit/core/retrieval/ -v
```

## License

EREN OS License
