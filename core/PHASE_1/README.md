# FASE 1: Business Domain

## Descripción

FASE 1 establece el dominio de negocio de EREN para Ingeniería Clínica. Aquí se encuentran todas las entidades, agregados, eventos de dominio y servicios que representan el mundo real de los hospitales y la gestión de equipos médicos.

## Estructura

```
core/PHASE_1/
├── README.md                    # Este archivo
│
├── domain/                     # Entidades de negocio (EPIC 2-3)
│   ├── asset/                 # Gestión de activos médicos
│   ├── capacity/             # Capacidad hospitalaria
│   ├── department/           # Departamentos
│   ├── device/               # Dispositivos médicos
│   ├── incident/            # Incidentes
│   ├── inventory/           # Inventario
│   ├── knowledge/           # Dominio de conocimiento
│   ├── models/              # Modelos de dominio
│   ├── organization/        # Organizaciones
│   └── staffing/            # Personal
│
├── infrastructure/            # Infraestructura compartida (EPIC 1)
│   ├── events/              # Sistema de eventos
│   ├── shared/             # Módulos compartidos
│   ├── lifecycle/           # Ciclo de vida
│   ├── boot/               # Bootstrapping
│   ├── container/          # Contenedor DI
│   ├── contracts/          # Contratos
│   ├── biomedical/         # Dominio biomédico
│   ├── diagnostic/         # Diagnóstico
│   └── diagnostics/        # Sistema de diagnósticos
│
├── clinical/                 # Clínica (EPIC 5)
│
├── application/              # Servicios de aplicación (EPIC 11)
│
└── workflows/                # Flujos de trabajo (EPIC 3)
    ├── workflow/
    ├── workflows/
    └── composition/
```

## EPICs Incluidos

| EPIC | Nombre | Descripción |
|------|--------|-------------|
| EPIC 0 | Architecture | Arquitectura y documentos base |
| EPIC 1 | Infrastructure | PostgreSQL, Redis, RabbitMQ, Docker |
| EPIC 2 | Shared Kernel | Contexto compartido de dominio |
| EPIC 3 | Device Context | Gestión de dispositivos médicos |
| EPIC 4 | Incident Context | Gestión de incidentes |
| EPIC 5 | Recommendation Context | Recomendaciones |
| EPIC 6 | Knowledge Context | Conocimiento institucional |
| EPIC 7 | APIs Base | Contratos de API |
| EPIC 8 | Security Base | Seguridad base |
| EPIC 9 | Consolidation | Consolidación |
| EPIC 11 | Application Services | Servicios de aplicación |

## Tests

Los tests correspondientes se encuentran en:

```
tests/unit/PHASE_1/
├── domain/          # Tests de entidades de negocio
├── infrastructure/  # Tests de infraestructura
├── clinical/       # Tests clínicos
├── application/   # Tests de aplicación
└── workflows/      # Tests de workflows
```

## Documentación Relacionada

- [docs/phases/PHASE_1/](../../docs/phases/PHASE_1/)
- [docs/phases/PHASE_1/epics/](../../docs/phases/PHASE_1/epics/)
- [docs/phases/PHASE_1/adr/](../../docs/phases/PHASE_1/adr/)

---

*Última actualización: 2026-07-22*
