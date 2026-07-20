# Embedding Provider Layer (EPL)

> **EREN's official abstraction layer for embedding generation.**

This layer provides a unified interface for generating embeddings without coupling to specific providers.

## Philosophy

Conversational models generate responses.

Embedding models generate vector representations.

The Kernel Cognitivo never knows a specific embedding provider.

All embedding generation occurs through common contracts.

## Responsibilities

The EPL is responsible only for:
- **Selecting providers** based on policies
- **Generating embeddings** through provider interface
- **Managing health checks**
- **Estimating costs**
- **Recording metrics**

## Architecture

```
Semantic Retrieval Engine
        │
        ▼
Embedding Manager
        │
        ▼
Embedding Selector
        │
        ▼
Embedding Registry
        │
        ▼
Embedding Providers
        │
   ┌────┼────┬─────────┐
   ▼    ▼    ▼         ▼
OpenAI Gemini Ollama  Custom
```

## Components

| Component | Description |
|-----------|-------------|
| `manager.py` | Main interface for embeddings |
| `provider.py` | Provider interface |
| `registry.py` | Provider registration |
| `selector.py` | Provider selection |
| `configuration.py` | Configuration |
| `types.py` | Types and models |
| `exceptions.py` | Exception types |
| `metrics.py` | Metrics collection |
| `events.py` | Event bus |
| `trace.py` | Operation tracing |

## Providers

| Provider | Description |
|----------|-------------|
| `OPENAI` | OpenAI embeddings |
| `GEMINI` | Google Gemini embeddings |
| `OLLAMA` | Ollama local embeddings |
| `SENTENCE_TRANSFORMERS` | HuggingFace models |
| `AZURE_OPENAI` | Azure OpenAI |
| `CUSTOM` | Custom provider |

## Policies

| Policy | Description |
|--------|-------------|
| `DEFAULT` | Use default provider |
| `CHEAPEST` | Use cheapest provider |
| `FASTEST` | Use fastest provider |
| `LOCAL_ONLY` | Use only local providers |
| `CLOUD_ONLY` | Use only cloud providers |
| `FAILOVER` | Failover to next provider |
| `ROUND_ROBIN` | Rotate through providers |
| `HEALTHY_FIRST` | Use healthy providers first |

## Usage

### Basic Usage

```python
from core.embeddings import (
    EmbeddingManager,
    EmbeddingProvider,
)

# Create manager
manager = EmbeddingManager()

# Register providers
from core.embeddings import OpenAIEmbeddingProvider, OllamaEmbeddingProvider

manager.registry.register(OpenAIEmbeddingProvider(), set_default=True)
manager.registry.register(OllamaEmbeddingProvider())

# Generate embeddings
response = await manager.embed(
    texts=["Hello world", "How are you?"],
    model="text-embedding-3-small",
)
```

### Single Embedding

```python
embedding = await manager.embed_single(
    text="Hello world",
    model="text-embedding-3-small",
)
print(embedding.vector)
```

### Policy Selection

```python
from core.embeddings import EmbeddingPolicy

# Use cheapest provider
response = await manager.embed(
    texts=["Hello world"],
    policy=EmbeddingPolicy.CHEAPEST,
)

# Use local provider
response = await manager.embed(
    texts=["Hello world"],
    policy=EmbeddingPolicy.LOCAL_ONLY,
)
```

### Health Check

```python
health = await manager.health_check()
print(health)
```

### Cost Estimation

```python
cost = manager.estimate_cost(
    texts=["Hello world", "How are you?"],
    model="text-embedding-3-small",
)
print(f"Estimated cost: ${cost:.6f}")
```

## Capabilities

- ✅ Generate embedding
- ✅ Generate batch embeddings
- ✅ Query dimensions
- ✅ Query model
- ✅ Health check
- ✅ Cost estimation
- ✅ Streaming (if applicable)

## Not Implemented

- Vector DB integration
- Chunking
- RAG
- Ranking

Only embedding generation.

## Testing

```bash
pytest tests/unit/core/embeddings/ -v
```

## License

EREN OS License
