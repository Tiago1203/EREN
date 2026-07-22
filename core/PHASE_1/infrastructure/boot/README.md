# core/boot - Cognitive Boot Manager

## Descripción

El **Cognitive Boot Manager** es responsable de iniciar EREN OS de manera ordenada y reproducible.

## Responsabilidad

- Coordenar la secuencia de boot
- Validar contratos antes del boot
- Publicar eventos de boot
- Soportar rollback en caso de fallo

## Arquitectura

```
Boot Manager
    │
    ├── Configuration Loader
    ├── Event Bus Creator
    ├── Capability Registry Creator
    ├── Context Manager Creator
    ├── Memory Engine Creator
    └── Knowledge Engine Creator
```

## Componentes

| Componente | Propósito |
|-----------|-----------|
| BootManager | Orquestador de boot |
| BootPolicy | Políticas de boot |
| BootEvents | Publicación de eventos |
| BootMetrics | Métricas de boot |

## Uso

```python
from core.boot import CognitiveBootManager

manager = CognitiveBootManager()
result = manager.boot()
```

## Límites

- **Puede depender de:** container, events, capabilities
- **Nunca depende de:** apps, UI

---

*Architecture only - no business logic*
