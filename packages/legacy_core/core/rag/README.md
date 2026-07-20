# core/rag - RAG Pipeline

## Descripción

Pipeline de Retrieval-Augmented Generation.

## Responsabilidad

- Retrieval de documentos
- Construcción de contexto
- Integración con providers

## Arquitectura

```
RAG Pipeline
    │
    ├── Retrieval
    ├── Context Builder
    ├── Prompt Builder
    └── Response Builder
```

## Límites

- **Puede depender de:** retrieval, providers, memory
- **Nunca depende de:** implementaciones específicas

---
*Architecture only*
