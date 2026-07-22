# core/container - Cognitive Dependency Injection Container

## Descripción

El **Cognitive DI Container** proporciona inyección de dependencias para EREN OS.

## Responsabilidad

- Registrar servicios
- Resolver dependencias
- Crear scopes
- Detectar dependencias circulares

## Arquitectura

```
Container
    │
    ├── Service Registry
    ├── Service Provider
    ├── Dependency Graph
    ├── Dependency Validator
    └── Service Scope
```

## Uso

```python
from core.container import CognitiveContainer

container = CognitiveContainer()
container.register("IEventBus", EventBus)
```

## Límites

- **Puede depender de:** contracts
- **Nunca depende de:** business logic

---
*Architecture only - no business logic*
