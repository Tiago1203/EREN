# core/lifecycle - Lifecycle Manager

## Descripción

Gestión del ciclo de vida de componentes en EREN OS.

## Responsabilidad

- Inicializar componentes
- Gestionar estados
- Cleanup en shutdown

## Arquitectura

```
Lifecycle Manager
    │
    ├── Initialization
    ├── State Management
    ├── Health Monitoring
    └── Shutdown Handler
```

## Estados

- CREATED → INITIALIZING → READY → STOPPING → STOPPED

## Límites

- **Puede depender de:** events, container
- **Nunca depende de:** business logic

---
*Architecture only*
