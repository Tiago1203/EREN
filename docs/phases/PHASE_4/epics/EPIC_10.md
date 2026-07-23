# EPIC 10: Knowledge Synchronization Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Mantener actualizado el conocimiento biomédico.

---

## Responsabilidad

**Sincronizar automáticamente nuevas publicaciones y fuentes.**

EPIC 10 es responsable de:
- Gestionar sincronización de fuentes
- Programar actualizaciones
- Monitorear salud de fuentes
- Detectar cambios en fuentes
- Procesar deltas de actualización

---

## Dependencias

### EPICs
- **EPIC 9**: Consume Medical Knowledge Repository

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│          EPIC 10: Knowledge Synchronization Engine                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     Repository (from EPIC 9)                           │   │
│  │     External Sources (PubMed, FDA, etc.)               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        SYNC                                │   │
│  │  ├── SyncJob ───────────────────────► Sync job model     │   │
│  │  ├── InMemorySyncManager ───────────► Manage sync       │   │
│  │  ├── UpdatePackage ─────────────────► Update package     │   │
│  │  └── DeltaProcessor ────────────────► Process deltas      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      SCHEDULE                               │   │
│  │  ├── ScheduleConfig ────────────────► Schedule config     │   │
│  │  ├── InMemoryScheduler ────────────► Schedule jobs       │   │
│  │  └── CronParser ───────────────────► Parse cron expr     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       MONITOR                               │   │
│  │  ├── SourceHealth ─────────────────► Health status       │   │
│  │  ├── InMemorySourceMonitor ──────────► Monitor sources   │   │
│  │  ├── ChangeEvent ───────────────────► Change events      │   │
│  │  └── HealthChecker ──────────────────► Check health      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     Repository (permanently updated)                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic10_sync_engine/
├── __init__.py                    # Módulo principal
├── sync/                          # Sincronización
│   └── __init__.py              # SyncManager, SyncJob, etc.
├── schedule/                      # Programación
│   └── __init__.py             # Scheduler, ScheduleConfig, etc.
└── monitor/                     # Monitoreo
    └── __init__.py            # SourceMonitor, HealthChecker, etc.
```

---

## Componentes

### 1. Sync

| Componente | Descripción |
|------------|-------------|
| `SyncJob` | Trabajo de sincronización |
| `UpdatePackage` | Paquete de actualización |
| `SyncDelta` | Delta de cambios |
| `InMemorySyncManager` | Gestor de sincronización |
| `DeltaProcessor` | Procesador de deltas |

**Fuentes:**
- `PUBMED` - PubMed
- `FDA` - FDA
- `EMA` - EMA
- `CLINICAL_GUIDELINES` - Guidelines
- `DEVICE_MANUFACTURERS` - Manufacturers
- `STANDARDS_BODIES` - Standards

**Estados:**
- `PENDING` - Pendiente
- `IN_PROGRESS` - En progreso
- `COMPLETED` - Completado
- `FAILED` - Fallido
- `PARTIAL` - Parcial

### 2. Schedule

| Componente | Descripción |
|------------|-------------|
| `ScheduleConfig` | Configuración de programación |
| `ScheduledJob` | Trabajo programado |
| `InMemoryScheduler` | Scheduler en memoria |
| `CronParser` | Parser de expresiones cron |

**Frecuencias:**
- `HOURLY` - Cada hora
- `DAILY` - Diario
- `WEEKLY` - Semanal
- `MONTHLY` - Mensual
- `ON_DEMAND` - Bajo demanda

### 3. Monitor

| Componente | Descripción |
|------------|-------------|
| `SourceHealth` | Estado de salud |
| `ChangeEvent` | Evento de cambio |
| `InMemorySourceMonitor` | Monitor de fuentes |
| `HealthChecker` | Verificador de salud |
| `ChangeDetector` | Detector de cambios |

**Estados de salud:**
- `HEALTHY` - Saludable
- `DEGRADED` - Degradado
- `DOWN` - Caído
- `UNKNOWN` - Desconocido

---

## Uso

### Iniciar sincronización

```python
from core.PHASE_4.epic10_sync_engine import (
    InMemorySyncManager,
    SyncSource,
)

manager = InMemorySyncManager()

job = await manager.start_sync(SyncSource.PUBMED)
print(f"Started job: {job.job_id}")
```

### Programar sync

```python
from core.PHASE_4.epic10_sync_engine import (
    InMemoryScheduler,
    ScheduleConfig,
    ScheduleFrequency,
)

scheduler = InMemoryScheduler()

config = ScheduleConfig(
    schedule_id="daily_sync",
    frequency=ScheduleFrequency.DAILY,
    hour=2,  # 2 AM
    minute=0,
)

await scheduler.schedule(config)
```

### Monitorear fuentes

```python
from core.PHASE_4.epic10_sync_engine import (
    InMemorySourceMonitor,
    HealthChecker,
)

monitor = InMemorySourceMonitor()
checker = HealthChecker(monitor)

health = await checker.check("pubmed")
print(f"Status: {health.status}")
```

---

## Flujo de Sincronización

```
1. INPUT: Repository (from EPIC 9)
          │
          ▼
2. SCHEDULE: InMemoryScheduler
          │ Check due schedules
          │
          ▼
3. SYNC: InMemorySyncManager
          │ Start sync job
          │ Get deltas
          │
          ▼
4. MONITOR: InMemorySourceMonitor
          │ Check health
          │ Detect changes
          │
          ▼
5. DELTA: DeltaProcessor
          │ Process changes
          │ Apply updates
          │
          ▼
6. OUTPUT: Repository (updated)
          │
          ▼
7. NEXT: EPIC 11 (Knowledge Governance)
```

---

## Concatenación

```
EPIC 9 ──► EPIC 10 (consume Repository)
EPIC 0 ──► EPIC 10 (usa Foundation types)
EPIC 10 ──► EPIC 11 (provee SyncJob para governance)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 11: Knowledge Governance & Lifecycle

---

*EREN PHASE 4 - EPIC 10*
*Architecture Board - 2026-07-23*
