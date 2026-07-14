# core/composition - Cognitive Composition Root

## Descripción

El **Cognitive Composition Root** ensambla todos los componentes de EREN OS.

## Responsabilidad

- Construir el DI Container
- Registrar módulos
- Configurar Event Bus
- Validar el sistema

## Arquitectura

```
Composition Root
    │
    ├── Module Loader
    ├── Module Registry
    ├── Composition Builder
    └── Composition Validator
```

## Uso

```python
from core.composition import CognitiveCompositionRoot

root = CognitiveCompositionRoot().with_default_modules()
root.validate().build()
```

## Límites

- **Puede depender de:** container, boot, events
- **Nunca depende de:** business logic, apps

---
*Architecture only - no business logic*
