# core/execution - Execution Engine

## Descripción

Motor de ejecución de tareas y capabilities.

## Responsabilidad

- Ejecutar tareas
- Gestionar resultados
- Manejar timeouts

## Uso

```python
from core.execution import ExecutionEngine

engine = ExecutionEngine()
result = await engine.execute(task)
```

## Límites

- **Puede depender de:** tools, providers, events
- **Nunca depende de:** UI

---
*Architecture only*
