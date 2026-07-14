# core/pipeline - Processing Pipeline

## Descripción

Pipeline de procesamiento de datos.

## Responsabilidad

- Encadenar processors
- Gestionar flujo de datos
- Manejar errores de pipeline

## Arquitectura

```
Pipeline
    │
    ├── Pipeline Builder
    ├── Pipeline Executor
    ├── Processor Chain
    └── Error Handler
```

## Límites

- **Puede depender de:** events, contracts
- **Nunca depende de:** business logic

---
*Architecture only*
