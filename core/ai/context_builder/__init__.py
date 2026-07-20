"""EREN AI Context Builder - Context Builder Module.

Módulo de construcción de contexto del AI Core.

## Componentes

- **models**: Modelos de datos (ContextItem, ContextWindow, etc.)
- **prioritizer**: Priorizador de contexto
- **compressor**: Compresor de contexto
- **builder**: Constructor principal y ensamblador

## Fuentes de Contexto

El Context Builder integra información de:
- Conversation (EPIC 1)
- Memory (EPIC 4)
- Incidents (FASE 1)
- Devices (FASE 1)
- Knowledge (FASE 1)
- User
- Hospital
- Session

## Uso

```python
from core.ai.context_builder import (
    ContextBuilder,
    ContextAssembler,
    ContextConfig,
    ContextQuery,
    ContextSource,
    create_context_item,
)

# Configurar
config = ContextConfig(
    default_max_tokens=8192,
    compression_enabled=True,
)

# Crear builder
builder = ContextBuilder(config=config)

# Registrar fuentes
builder.register_source(
    ContextSource.CONVERSATION,
    get_conversation_context,
)

# Construir contexto
query = ContextQuery(
    conversation_id="conv-123",
    user_id="user-456",
    max_tokens=8192,
)

result = await builder.build(query)

# Ensamblar
assembler = ContextAssembler(config)
context_text = assembler.assemble(result)
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTEXT BUILDER                                  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Source Getters                           │ │
│  │  Conversation │ Memory │ Device │ Knowledge │ etc.        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Relevance Calculator                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Compressor                             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Prioritizer                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Context Window                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Assembler                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```
"""

from core.ai.context_builder.builder import (
    ContextAssembler,
    ContextBuilder,
    ContextSourceGetter,
    create_context_item,
)
from core.ai.context_builder.compressor import (
    CompressionStrategy,
    ContextCompressor,
    IntelligentCompressor,
    RemoveDuplicatesStrategy,
    RemoveRedundantInfoStrategy,
    SourceBasedCompressionStrategy,
    SummarizeStrategy,
    TrimWhitespaceStrategy,
)
from core.ai.context_builder.models import (
    ContextConfig,
    ContextItem,
    ContextPriority,
    ContextQuery,
    ContextResult,
    ContextSource,
    ContextSourceConfig,
    ContextWindow,
)
from core.ai.context_builder.prioritizer import (
    ContextPrioritizer,
    RelevanceCalculator,
    RelevanceStrategy,
    KeywordRelevance,
    RecencyRelevance,
    SemanticRelevance,
)

__version__ = "1.0.0"

__all__ = [
    # Builder
    "ContextBuilder",
    "ContextAssembler",
    "ContextSourceGetter",
    "create_context_item",
    # Compressor
    "ContextCompressor",
    "IntelligentCompressor",
    "CompressionStrategy",
    "RemoveDuplicatesStrategy",
    "TrimWhitespaceStrategy",
    "RemoveRedundantInfoStrategy",
    "SummarizeStrategy",
    "SourceBasedCompressionStrategy",
    # Models
    "ContextItem",
    "ContextWindow",
    "ContextQuery",
    "ContextResult",
    "ContextConfig",
    "ContextSource",
    "ContextPriority",
    "ContextSourceConfig",
    # Prioritizer
    "ContextPrioritizer",
    "RelevanceCalculator",
    "RelevanceStrategy",
    "KeywordRelevance",
    "RecencyRelevance",
    "SemanticRelevance",
]
