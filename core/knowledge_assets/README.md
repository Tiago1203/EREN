# core/knowledge_assets - Knowledge Asset Registry

## Descripción

Registro de assets de conocimiento para EREN OS.

## Responsabilidad

- Registrar knowledge assets
- Gestionar metadatos
- Versionar assets

## Arquitectura

```
Knowledge Asset Registry
    │
    ├── Asset Registry
    ├── Asset Metadata
    ├── Asset Versioning
    └── Asset Storage
```

## Límites

- **Puede depender de:** events, storage
- **Nunca depende de:** UI

---
*Architecture only*
