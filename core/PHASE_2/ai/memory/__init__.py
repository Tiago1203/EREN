"""EREN AI Memory - Memory Manager Module.

Módulo de gestión de memoria del AI Core.

## Tipos de Memoria

- **Working Memory**: Memoria de trabajo activa para la sesión actual
- **Short Memory**: Memoria a corto plazo (días)
- **Long Memory**: Memoria a largo plazo (semanas/meses)
- **Episodic Memory**: Memoria de experiencias y eventos
- **Semantic Memory**: Memoria de conocimiento general

## Funciones

- **Guardar**: Almacenar nuevos recuerdos
- **Recuperar**: Buscar y obtener memorias
- **Resumir**: Generar resúmenes de memorias
- **Olvidar**: Eliminar o marcar memorias para olvido
- **Consolidar**: Fortalecer memorias importantes

## Uso

```python
from core.PHASE_2.ai.memory import MemoryManager, MemoryType, MemoryImportance

# Crear manager
manager = MemoryManager()

# Guardar memoria
item = manager.store(
    content="El usuario prefiere respuestas cortas",
    memory_type=MemoryType.SEMANTIC,
    user_id="user-123",
    tags=["preferencia", "usuario"],
)

# Recuperar
item = manager.retrieve(item.id)

# Buscar
results = manager.search(
    query="preferencias",
    memory_type=MemoryType.SEMANTIC,
    user_id="user-123",
)

# Consolidar (fortalecer)
manager.consolidate(item.id, level=0.9)

# Olvidar
manager.forget(old_item.id)

# Resumir
summary = manager.summarize(MemoryType.SEMANTIC, user_id="user-123")
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     MEMORY MANAGER                                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Memory Repository                         │ │
│  │        (Abstract + InMemory Implementation)               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Memory Types                              │ │
│  │  Working │ Short │ Long │ Episodic │ Semantic            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Operations                               │ │
│  │    store │ retrieve │ summarize │ forget │ consolidate     │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```
"""

from core.PHASE_2.ai.memory.manager import MemoryManager
from core.PHASE_2.ai.memory.models import (
    MemoryConfig,
    MemoryEvent,
    MemoryEventType,
    MemoryImportance,
    MemoryItem,
    MemoryQuery,
    MemoryResult,
    MemorySummary,
    MemoryType,
)
from core.PHASE_2.ai.memory.repository import InMemoryMemoryRepository, MemoryRepository

__version__ = "1.0.0"

__all__ = [
    # Manager
    "MemoryManager",
    # Models
    "MemoryItem",
    "MemoryQuery",
    "MemoryResult",
    "MemorySummary",
    "MemoryConfig",
    "MemoryEvent",
    "MemoryEventType",
    "MemoryImportance",
    "MemoryType",
    # Repository
    "MemoryRepository",
    "InMemoryMemoryRepository",
]
