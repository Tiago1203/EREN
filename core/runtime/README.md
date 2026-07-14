# core/runtime - Runtime Engine

## Descripción

El **Runtime Engine** gestiona la ejecución de EREN OS en tiempo de ejecución.

## Responsabilidad

- Gestionar estado del runtime
- Ejecutar el ciclo cognitivo
- Monitorear salud
- Manejar errores

## Arquitectura

```
Runtime Engine
    │
    ├── Runtime State
    ├── Runtime Executor
    ├── Runtime Health
    ├── Runtime Metrics
    └── Runtime Trace
```

## Uso

```python
from core.runtime import CognitiveRuntime

runtime = CognitiveRuntime()
runtime.start()
```

## Límites

- **Puede depender de:** todos los módulos
- **Nunca depende de:** apps

---
*Architecture only - no business logic*
