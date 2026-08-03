# ARQUITECTURA OBJETIVO — EREN

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** Auditoría `docs/audit/` + Reglas Arquitectónicas `ARCHITECTURAL_RULES.md`

---

## PRINCIPIO FUNDADOR

> "EREN no es una API. EREN es un sistema con múltiples puntos de entrada: Web, API, Workers, CLI, Voice, Desktop, Agents."

Este principio define todo lo demás. Los Use Cases viven en core/, no en `apps/api/`. Cada entry point construye los mismos Use Cases.

---

## CAPAS ARQUITECTÓNICAS

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│  Web · API · CLI · Workers · Voice · Desktop · Agents         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ commands / queries
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                             │
│  Use Cases: CreateDevice · GenerateRecommendation · SearchKnowledge │
│  Cada entry point construye los mismos Use Cases                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ implements
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                                │
│  device · clinical · ai · audit · tenant · enterprise          │
│  Cada Bounded Context es independiente                         │
│  Define sus propios: entities, value objects, events, contracts │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ publishes / subscribes
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│  apps/                                                         │
│  repositories · event bus · cache · external clients           │
│  Implementan los contratos definidos en los Domains               │
└─────────────────────────────────────────────────────────────────┘
```

---

## ESTRUCTURA DE DIRECTORIOS

### core/ — Dominio

```
core/
├── device/                         # Bounded Context
│   ├── domain/
│   │   ├── entities/              # Device (AggregateRoot)
│   │   ├── value_objects/         # DeviceId, DeviceStatus
│   │   └── events/               # DeviceRegistered, MaintenanceScheduled
│   ├── application/               # CreateDevice, UpdateDevice, ScheduleMaintenance
│   ├── contracts/                  # DeviceRepository (Puerto público)
│   └── __init__.py
│
├── clinical/                      # Bounded Context
│   ├── domain/
│   │   ├── recommendation/
│   │   │   ├── entities/         # AIRecommendation (AggregateRoot)
│   │   │   ├── value_objects/    # ConfidenceLevel, RecommendationStatus
│   │   │   └── events/          # RecommendationGenerated
│   │   ├── reasoning/
│   │   ├── evidence/
│   │   └── safety/
│   ├── application/               # GenerateRecommendation, ValidateEvidence
│   ├── contracts/                  # RecommendationRepository
│   └── __init__.py
│
├── ai/                           # Bounded Context — Dominio técnico
│   ├── domain/
│   │   ├── embeddings/           # EmbeddingVector (Value Object)
│   │   ├── reasoning/           # ReasoningEngine (Entity)
│   │   ├── memory/              # SessionMemory (Entity)
│   │   ├── agents/              # AgentTask (AggregateRoot)
│   │   ├── planner/            # PlanStep (Value Object)
│   │   └── rag/                # RetrievalResult (Value Object)
│   ├── application/             # AnalyzeContext, GeneratePlan, ExecuteAgentTask
│   ├── contracts/               # EmbeddingPort, ReasoningPort, MemoryPort
│   └── __init__.py
│
├── audit/                        # Bounded Context
│   ├── domain/
│   │   ├── entities/            # AuditEntry (AggregateRoot)
│   │   └── events/             # ActionLogged
│   ├── application/            # LogAction, QueryAuditTrail
│   └── contracts/
│
├── tenant/                      # Bounded Context
│   ├── domain/
│   │   ├── entities/            # Tenant (AggregateRoot)
│   │   └── events/            # TenantCreated
│   ├── application/             # CreateTenant, ConfigureQuotas
│   └── contracts/
│
├── enterprise/                   # Bounded Context
│   ├── domain/
│   │   ├── compliance/
│   │   ├── licensing/
│   │   └── support/
│   ├── application/
│   └── contracts/
│
└── shared/                      # Elementos transversales
    ├── primitives/             # EntityId, AggregateRoot, ValueObject
    ├── result/                # Result[T, E], Ok, Err
    └── types/                  # Tipos transversales básicos
```

### apps/ — Presentación + Infraestructura

```
apps/
├── api/                         # Entry point: HTTP API
│   ├── presentation/
│   │   └── routers/           # FastAPI routers → Use Cases
│   ├── infrastructure/
│   │   ├── repositories/       # Implementaciones SQLAlchemy → DeviceRepository
│   │   ├── messaging/         # RabbitMQ + Transactional Outbox
│   │   ├── cache/             # Redis
│   │   └── adapters/        # Anti-Corruption Layer para AI
│   └── main.py               # Composition Root: factory functions
│
├── workers/                    # Entry point: Background workers (Celery)
│   ├── main.py               # Composition Root (mismos Use Cases)
│   ├── presentation/
│   └── infrastructure/
│
├── cli/                       # Entry point: Command line
│   ├── main.py
│   └── infrastructure/
│
└── web/                       # Entry point: Next.js SPA
    └── packages/sdk/           # Cliente tipado para apps/api
```

### platform/ — Operaciones

```
platform/
├── deployment/                # Scripts de deploy
├── monitoring/               # Prometheus + Grafana
├── logging/                  # ELK stack
├── observability/             # OpenTelemetry
├── recovery/                 # Backup + restore
└── scaling/                  # Autoscaling configs
```

---

## DOMINIOS Y SUS RESPONSABILIDADES

### device — Gestión de dispositivos clínicos

**Propósito:** Representar el mundo físico de dispositivos médicos.

**Entidades:**
- `Device` (AggregateRoot): dispositivo con serial, ubicación, estado
- `EngineeringIncident` (AggregateRoot): incidente generado por un dispositivo
- `WorkOrder` (AggregateRoot): orden de trabajo asociada a incidente
- `KnowledgeArticle` (AggregateRoot): documentación técnica

**Eventos de dominio:**
- `DeviceRegistered`
- `MaintenanceScheduled`
- `IncidentCreated`
- `WorkOrderCompleted`

**Contratos públicos:**
- `DeviceRepository`
- `IncidentRepository`
- `WorkOrderRepository`

**Dependencias permitidas:**
- Puede consumir `ai/` por eventos
- Publica eventos que otros domains consumen

---

### clinical — Inteligencia clínica

**Propósito:** Generar recomendaciones clínicas basadas en evidencia.

**Entidades:**
- `AIRecommendation` (AggregateRoot): recomendación con nivel de confianza
- `Evidence` (Entity): evidencia que soporta una recomendación
- `ReasoningResult` (Value Object): resultado de un pipeline de razonamiento

**Eventos de dominio:**
- `RecommendationGenerated`
- `EvidenceValidated`
- `ReasoningCompleted`

**Contratos públicos:**
- `RecommendationRepository`
- `ReasoningPipeline` (Puerto para invocar reasoning)

**Dependencias permitidas:**
- Consume `device/` por eventos (`DeviceRegistered`, `IncidentCreated`)
- Consume `ai/` por gateway
- Publica `RecommendationGenerated`

---

### ai — Dominio técnico de inteligencia

**Propósito:** Proveer capacidades de inteligencia: embeddings, razonamiento, memoria, planificación.

**Entidades:**
- `CognitiveSession` (AggregateRoot): sesión de interacción con el sistema
- `AgentTask` (AggregateRoot): tarea asignada a un agente
- `EmbeddingVector` (Value Object): vector de embedding
- `PlanStep` (Value Object): paso de un plan generado

**Eventos de dominio:**
- `EmbeddingGenerated`
- `PlanExecuted`
- `MemoryUpdated`

**Contratos públicos (Puertos de AI):**
- `EmbeddingPort`: generar embeddings para textos
- `ReasoningPort`: ejecutar pipelines de razonamiento
- `MemoryPort`: almacenar y recuperar memoria de sesión
- `RetrievalPort`: búsqueda semántica

**Dependencias permitidas:**
- Consume `device/` y `clinical/` por eventos
- Expone capacidades a `clinical/` y `enterprise/` por gateways

**Nota:** Para EREN, AI es el producto. No es infraestructura. Los embeddings y razonadores son dominio.

---

### audit — Auditoría

**Propósito:** Registrar todas las acciones del sistema para cumplimiento regulatorio.

**Entidades:**
- `AuditEntry` (AggregateRoot): registro de auditoría

**Eventos de dominio:**
- `ActionLogged`

**Dependencias permitidas:**
- Consume eventos de TODOS los otros domains
- No publica eventos

---

### tenant — Multi-tenancy

**Propósito:** Aislar tenants y gestionar cuotas.

**Entidades:**
- `Tenant` (AggregateRoot): tenant con configuración
- `Quota` (Value Object): límite de recursos

**Eventos de dominio:**
- `TenantCreated`

**Dependencias permitidas:**
- No consume otros domains

---

## RELACIONES ENTRE DOMINIOS

```
device
    ├── publishes → DeviceRegistered, MaintenanceScheduled, IncidentCreated
    └── consumed_by → clinical, audit

clinical
    ├── subscribes → DeviceRegistered, IncidentCreated
    ├── consumes → ai (via gateway)
    ├── publishes → RecommendationGenerated
    └── consumed_by → audit

ai
    ├── subscribes → DeviceRegistered, IncidentCreated
    ├── publishes → EmbeddingGenerated, PlanExecuted
    └── consumed_by → clinical (via gateway)

audit
    └── subscribes → TODOS los eventos

tenant
    └── isolated — no subscribe a eventos de otros domains
```

---

## FLUJO DE UN CASO DE USO: Registrar dispositivo

```
1. API recibe POST /devices (presentation)
2. Router llama CreateDeviceUseCase (application)
3. CreateDeviceUseCase ejecuta Device.create() (domain)
4. DeviceRepository.save() persiste (infrastructure)
5. DeviceRepository publica DeviceRegistered event (domain event)
6. Event Bus distribuye el evento
7. clinical.subsystem recibe DeviceRegistered
   → Trigger: GenerateRecommendationUseCase
8. audit.subsystem recibe DeviceRegistered
   → Log: AuditEntry.create(device_id=...)
9. API retorna DeviceCreated (presentation)
```

Este flujo usa los mismos Use Cases que Worker o CLI.

---

## FLUJO DE UN CASO DE USO: Generar recomendación

```
1. AI.subsystem recibe DeviceRegistered event
2. AI_embedding_port.get_embeddings(texts)
3. AI_retrieval_port.search(query, top_k=10)
4. AI_reasoning_port.validate(claim, evidence)
5. AIRecommendation.create(confidence, evidence, explanation)
6. RecommendationRepository.save(recommendation)
7. RecommendationGenerated event publicado
8. Worker recibe el evento → Envía notificación
9. Audit recibe el evento → Registra acción
```

---

## COMPOSITION ROOT

Cada entry point define su propio Composition Root:

```
apps/api/main.py         → factory functions: create_device_service()
apps/workers/main.py     → factory functions: create_device_service()
apps/cli/main.py         → factory functions: create_device_service()
```

Todos construyen los mismos Use Cases con diferentes implementaciones de infraestructura.

---

## MIGRACIÓN DESDE EL ESTADO ACTUAL

### Lo que cambia

```
PHASE_1           → device/
PHASE_3           → clinical/
PHASE_2           → ai/
PHASE_7/audit     → audit/
PHASE_7/tenant    → tenant/
PHASE_7/compliance → enterprise/
PHASE_5           → ai/agents/ (integración via gateways)
PHASE_7/infra     → platform/
```

### Lo que no cambia

- La lógica de negocio ya implementada permanece
- Los tests existentes siguen pasando
- Los endpoints de API mantienen sus paths
- Las migraciones de base de datos son las mismas

### Lo que se elimina

- Código muerto identificado en la auditoría
- Carpetas ceremoniales vacías
- Nombres PHASE_1, PHASE_2, etc.

---

*Esta arquitectura es el estado objetivo. La migración física se planifica en MIGRATION_PRINCIPLES.md.*
