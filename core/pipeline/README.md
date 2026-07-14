# core/pipeline - Processing Pipeline

## Descripción

Pipeline de procesamiento de datos que incluye el Cognitive Pipeline (PR-048) para ejecución del ciclo cognitivo completo de EREN OS.

## Responsabilidad

- Encadenar processors
- Gestionar flujo de datos
- Manejar errores de pipeline
- Ejecutar el ciclo cognitivo completo

## Arquitectura

```
Pipeline
│
├── Pipeline Builder
├── Pipeline Executor
├── Processor Chain
├── Error Handler
│
└── Cognitive Pipeline (PR-048)
    │
    ├── IntentDetectionStage
    ├── ContextBuildingStage
    ├── MemoryRetrievalStage
    ├── KnowledgeRetrievalStage
    ├── CognitiveReasoningStage
    ├── CognitivePlanningStage
    ├── CognitiveDecisionStage
    ├── TaskExecutionStage
    ├── CognitiveLearningStage
    └── ResponseGenerationStage
```

## Cognitive Pipeline

El Cognitive Pipeline implementa el ciclo cognitivo completo:

1. **Intent Detection** → Detecta la intención del usuario
2. **Context Building** → Construye el contexto de procesamiento
3. **Memory Retrieval** → Recupera memorias relevantes
4. **Knowledge Retrieval** → Recupera conocimiento relevante
5. **Reasoning** → Realiza razonamiento sobre la entrada
6. **Planning** → Crea un plan de ejecución
7. **Decision Making** → Toma decisiones basadas en el análisis
8. **Execution** → Ejecuta las tareas planificadas
9. **Learning** → Aprende de la ejecución
10. **Response Generation** → Genera la respuesta final

## Uso

```python
from core.pipeline import (
    create_cognitive_pipeline,
    CognitiveEventPublisher,
)

# Crear publisher de eventos
publisher = CognitiveEventPublisher()

# Crear pipeline cognitivo
pipeline = create_cognitive_pipeline(event_publisher=publisher)

# Ejecutar
result = pipeline.execute(user_input="¿Cuál es el clima?")

print(result.response["text"])
```

## Límites

- **Puede depender de:** events, contracts, memory, knowledge, reasoning, planning
- **Nunca depende de:** business logic, modelos concretos

## Eventos

El Cognitive Pipeline emite:
- `PIPELINE_STARTED` / `PIPELINE_COMPLETED` / `PIPELINE_FAILED`
- `INTENT_DETECTED` / `CONTEXT_BUILT` / `MEMORY_RETRIEVED`
- `KNOWLEDGE_RETRIEVED` / `REASONING_COMPLETED` / `PLAN_CREATED`
- `DECISION_MADE` / `EXECUTION_COMPLETED` / `LEARNING_COMPLETED`
- `RESPONSE_GENERATED`

---
*Architecture only*
*PR-048: Cognitive Runtime Implementation*
