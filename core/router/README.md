# core/router - Request Router

## Descripción

Sistema de enrutamiento de requests en EREN.

## Responsabilidad

- Enrutar requests
- Seleccionar capabilities
- Gestionar políticas de routing

## Arquitectura

```
Router
    │
    ├── Route Registry
    ├── Route Matcher
    ├── Policy Manager
    └── Metrics
```

## Límites

- **Puede depender de:** capabilities, events
- **Nunca depende de:** business logic

---
*Architecture only*
