# LEGACY: Módulos Sin Clasificar

## Descripción

Este directorio contiene módulos que no han sido clasificados en ninguna fase específica. Estos módulos fueron creados durante el desarrollo inicial pero no tienen documentación en EPICs o ADRs.

## Estructura

```
core/LEGACY/
├── README.md                    # Este archivo
│
├── collaboration/              # Sistema de colaboración
│   ├── aggregator.py
│   ├── communication_bus.py
│   ├── consensus.py
│   ├── dispatcher.py
│   ├── engine.py
│   ├── events.py
│   ├── messaging.py
│   ├── protocol.py
│   ├── resolver.py
│   ├── sessions.py
│   ├── shared_context.py
│   └── types.py
│
└── tools/                       # Sistema de herramientas
    ├── catalog/
    ├── discovery.py
    ├── engine.py
    ├── exceptions.py
    ├── execution.py
    ├── interfaces.py
    ├── models.py
    ├── sandbox.py
    ├── tool_descriptor.py
    ├── tool_executor.py
    ├── tool_pipeline.py
    ├── tool_registry.py
    ├── tool_types.py
    └── validation.py
```

## Estado

⚠️ **HUÉRFANOS**: Estos módulos NO están documentados en ningún EPIC o ADR.

## Acciones Posibles

1. **Documentar**: Crear EPIC y ADRs para estos módulos si son necesarios
2. **Archivar**: Mantener aquí indefinidamente
3. **Eliminar**: Si no se usan, eliminar del proyecto

## Decisión Pendiente

Waiting for decision from Architecture Board.

---

*Última actualización: 2026-07-22*
