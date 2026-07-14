# core/plugins - Plugin Framework

## Descripción

Framework para extender EREN con plugins.

## Responsabilidad

- Cargar plugins
- Gestionar lifecycle de plugins
- Aislamiento de plugins

## Arquitectura

```
Plugin Framework
    │
    ├── Plugin Loader
    ├── Plugin Registry
    ├── Plugin Manager
    └── Plugin Security
```

## Límites

- **Puede depender de:** container, events
- **Nunca depende de:** implementaciones

---
*Architecture only*
