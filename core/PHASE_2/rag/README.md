# core/rag - RAG Pipeline

> **Status:** IMPLEMENTED ✅

## Descripción

Pipeline de Retrieval-Augmented Generation para conocimiento de ingeniería clínica.

## Responsabilidad

- Retrieval de documentos
- Construcción de contexto
- Integración con providers
- Construcción de citas

## Arquitectura

```
RAG Pipeline
    │
    ├── Context Builder (Cognitive Context Engine)
    ├── Retrieval
    ├── Prompt Builder
    ├── Generator (LLM)
    └── Response Builder
```

## Componentes Implementados

| Componente | Responsabilidad |
|------------|-----------------|
| `pipeline.py` | Orquestación del pipeline RAG |
| `context_builder.py` | Construcción de contexto desde items recuperados |
| `prompt_builder.py` | Construcción de prompts desde contexto |
| `response_builder.py` | Construcción de respuestas finales |
| `citation_builder.py` | Generación de citas |
| `reranker.py` | Lógica de reranking |
| `token_budget.py` | Gestión de presupuesto de tokens |
| `hybrid_retrieval.py` | Retrieval híbrido |
| `types.py` | Definiciones de tipos |
| `exceptions.py` | Definiciones de errores |

## Características Implementadas

### Retrieval
- Retrieval denso (embeddings)
- Retrieval disperso (BM25)
- Retrieval híbrido
- Late interaction (ColBERT)

### Procesamiento
- Query processing y expansión
- Chunking semántico
- Reranking (cross-encoder)
- Gestión de presupuesto de tokens
- Deduplicación multi-fuente

## Uso

```python
from core.rag import CognitiveRAGPipeline

pipeline = CognitiveRAGPipeline()
result = await pipeline.query(
    question="How to troubleshoot device X?",
    user_id="user-123",
    conversation_id="conv-123",
)

print(result.response.answer)
print(f"Citations: {result.response.citations}")
print(f"Generation time: {result.response.generation_time_ms}ms")
```

## Estadísticas

```python
stats = pipeline.get_statistics()
print(f"Queries: {stats.queries_processed}")
print(f"Success rate: {stats.successful_queries / stats.queries_processed}")
```

## Límites

- **Puede depender de:** retrieval, providers, memory
- **Nunca depende de:** implementaciones específicas

---
*EREN RAG Pipeline v1.0*
