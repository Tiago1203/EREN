# PROJECT INVENTORY — Inventario Completo del Proyecto

**Fecha:** 2026-08-03
**Base:** 2,436 archivos fuente

---

## 1. ESTADÍSTICAS GLOBALES

| Tipo | Cantidad | Ubicación |
|---|---|---|
| Archivos Python (.py) | 1,553 | Distribuidos en todo el repo |
| Archivos TypeScript (.ts) | 99 | apps/web, packages |
| Archivos TSX (.tsx) | 77 | apps/web/components, modules |
| Archivos Markdown (.md) | 690 | docs/, docs/phases/, README.md |
| Archivos YAML (.yml/.yaml) | 17 | infra/, .github/workflows/ |
| Archivos de configuración | 8 | pyproject.toml (3), package.json, docker-compose.yml, etc. |

**Total archivos fuente: 2,436**

---

## 2. DESGLOSE POR ÁREA

### 2.1 apps/ — Entry Points

```
apps/
├── api/              180 .py     EN PRODUCCIÓN (API backend)
├── web/             176 .ts/.tsx  EN PRODUCCIÓN (frontend Next.js)
├── desktop/           1 .ts     SIN USO — stub
└── mobile/            1 .py     SIN USO — stub
```

**apps/api/** — FastAPI Backend
| Categoría | Archivos | Estado |
|---|---|---|
| Routers | 22 .py | EN PRODUCCIÓN |
| Schemas | 20 .py | EN PRODUCCIÓN |
| Domain (services, repos) | 25 .py | EN PRODUCCIÓN |
| Infrastructure (repos, messaging, models) | 35 .py | EN PRODUCCIÓN |
| Middleware | 4 .py | EN PRODUCCIÓN |
| Tasks (Celery) | 4 .py | PARCIAL — configured but not active |
| Integrations | 4 .py | PARCIAL |
| Providers | 3 .py | PARCIAL |
| Tests | 19 .py | PARCIAL — some failing |
| Migrations | 8 .py | EN PRODUCCIÓN |
| Core/Scripts/Enterprise/Events/Models | 36 .py | PARCIAL |

**apps/web/** — Next.js Frontend
| Categoría | Archivos | Estado |
|---|---|---|
| Pages (dashboard) | 14 .tsx | EN PRODUCCIÓN |
| Modules | 12 folders | EN PRODUCCIÓN |
| Components | 30+ .tsx | EN PRODUCCIÓN |
| Hooks | 15 .ts | EN PRODUCCIÓN |
| Services | 8 .ts | PARCIAL — 20 Supabase direct accesses |
| Tests | 8 .test.* | PARCIAL |
| lib/ (queries, storage, supabase) | 5 .ts | PROBLEMA — Supabase directo |

### 2.2 core/ — Cognitive Core

```
core/
├── PHASE_1/         1,154 .py  PARCIAL — domain real, infrastructure mezclada
├── PHASE_2/           ~600 .py  PARCIAL — mucho scaffolding, runtime dead
├── PHASE_3/           ~200 .py  PARCIAL — usado por apps/api
├── PHASE_4/           ~150 .py  PARCIAL — imports problemáticos a PHASE_2
├── PHASE_5/           ~200 .py  SIN INTEGRAR — placeholders, no conectado
├── PHASE_7/           ~150 .py  PARCIAL — sin uso en producción
├── PHASE_6/             0 .py   VACÍO — carpeta sin archivos
└── LEGACY/             ~20 .py  DEAD CODE — 0 imports externos
```

**Total estimado core/: ~2,500 .py**

### 2.3 tests/

```
tests/
├── unit/              150+ .py   PARCIAL — errors de colección en PHASE_1, 2
├── integration/        5 .py     PARCIAL
├── ai_core/            2 .py     PARCIAL
└── runtime/            2 .py     DEAD CODE — PHASE_2 runtime no usado
```

**apps/api/tests/** (separado)
```
apps/api/tests/
├── unit/              12 .py
└── integration/        3 .py
```

**apps/web/tests/**
```
apps/web/tests/
└── unit/              8 .test.*  (TypeScript)
```

### 2.4 packages/

```
packages/
├── sdk/                1 .ts      SIN USO — stub vacío
├── schemas/            1 .ts      SIN USO — stub vacío
├── prompts/           1 .ts      SIN USO — stub vacío
└── shared/            1 .ts      SIN USO — stub vacío
```

### 2.5 docs/

```
docs/
├── root/               4 .md     README, VISION, TECH_STACK, MANIFESTO
├── adr/               12 .md     ADR registry + _archive/
├── phases/           492 .md     Epics + ADRs por fase
├── architecture/     48 .md     Reportes, diagramas, guías
├── roadmap/           3 .md
├── guides/            3 .md
├── _archive/          ~50 .md   Archivos obsoletos
└── auditoria/        1 .md     (no existe aún)
```

### 2.6 infra/

```
infra/
├── k8s/               5 archivos      K8s manifests
├── helm/eren-api/     ~10 archivos     Helm chart
├── production/        6 .py           Scripts de producción
└── scripts/           3 .sh           Deploy, backup, rollback
```

### 2.7 .github/workflows/

```
.github/workflows/
└── ci.yml             1 archivo       Lint + typecheck (NO corre tests)
```

---

## 3. DESGLOSE DETALLADO: apps/api/app/

```
apps/api/app/
├── __init__.py
├── main.py                          ✅ EN PRODUCCIÓN
│   Evidence: uvicorn app:app, docker-compose reference
│
├── api/v1/                          ✅ EN PRODUCCIÓN (6 submódulos)
│   ├── admin/
│   ├── audit/
│   ├── compliance/
│   ├── tenants/
│   └── users/
│
├── config/                          ✅ EN PRODUCCIÓN
│   └── settings.py                 — Pydantic settings
│
├── core/                            ✅ EN PRODUCCIÓN
│   ├── database.py                 — AsyncSession, get_db
│   ├── exceptions.py
│   ├── logging.py
│   ├── config/ (empty)
│   └── security/
│
├── domain/                         ✅ EN PRODUCCIÓN — Application Services
│   ├── device/                     ✅ device/repository.py + service.py + cache.py + events.py
│   ├── incident/                  ✅ incident/repository.py
│   ├── work_order/                ✅ work_order/repository.py + service.py + events.py
│   ├── recommendation/             ✅ recommendation/repository.py
│   ├── knowledge/                 ✅ knowledge/repository.py
│   ├── department/                ⚠️ SIN USO — domain/repository.py existe, no usado
│   ├── inventory/                ⚠️ SIN USO
│   ├── organization/             ⚠️ SIN USO
│   ├── staffing/                 ⚠️ SIN USO
│   ├── capacity/                  ⚠️ SIN USO
│   └── asset/                     ⚠️ SIN USO
│
├── infrastructure/                 ✅ EN PRODUCCIÓN (parcial)
│   ├── repositories/              ✅ device, incident, knowledge, recommendation
│   │   ├── device.py              ✅ USADO por routers
│   │   ├── incident.py           ✅ USADO por routers
│   │   ├── knowledge.py          ✅ USADO por routers
│   │   ├── recommendation.py     ✅ USADO por routers
│   │   └── __init__.py
│   ├── messaging/                ✅ rabbitmq.py + outbox.py + cache.py
│   │   ├── rabbitmq.py           ✅ CONNECTED — outbox worker usa get_event_bus()
│   │   ├── outbox.py              ✅ CONNECTED — TransactionalOutbox.run() polling
│   │   └── cache.py              ✅ CONNECTED — Redis cache en routers
│   ├── models/                   ✅ 13 SQLAlchemy models
│   ├── observability/            ✅ logging.py + tracing.py
│   ├── vault/                    ⚠️ STUB — client.py existe, no usado
│   ├── events.py                 ⚠️ DUPLICADO — wrapper de EventBus
│   └── unit_of_work.py           ❌ DEAD CODE — nunca usado en routers
│
├── integrations/                   ⚠️ PARCIAL
│   ├── mqtt_client.py             ⚠️ STUB — existe pero no usado
│   ├── dicom_client.py            ⚠️ STUB — existe pero no usado
│   ├── hl7_listener.py            ⚠️ STUB — existe pero no usado
│   └── fhir_client.py             ⚠️ STUB — existe pero no usado
│
├── providers/                      ⚠️ PARCIAL
│   ├── circuit_breaker.py         ❌ DEAD CODE — nunca usado
│   └── security/
│       └── supabase_auth.py       ✅ USADO por middleware
│
├── middleware/                     ✅ EN PRODUCCIÓN
│   ├── authentication.py          ✅ — usa core/PHASE_1 contracts
│   ├── audit.py                  ✅ — usa core/PHASE_1 contracts
│   ├── request_context.py         ✅
│   └── __init__.py
│
├── models/                         ⚠️ DUPLICADO
│   ├── base.py                   ⚠️ — ¿diferente de infrastructure/models/base.py?
│   ├── diagnosis.py               ⚠️ — ¿por qué existe en apps/api?
│   └── patient.py                 ⚠️ — ¿por qué existe en apps/api?
│
├── routers/                       ✅ EN PRODUCCIÓN
│   ├── __init__.py               ✅ — api_router con 22 routers
│   ├── devices.py                ✅ — full CRUD + lifecycle
│   ├── work_orders.py            ✅
│   ├── incidents.py              ⚠️ — NO EXISTE como archivo independiente
│   ├── diagnosis.py              ⚠️ — ¿de dónde viene?
│   ├── health.py                 ✅
│   ├── auth.py                   ✅
│   ├── patients.py               ⚠️ — SIN USO claro
│   ├── organizations.py          ⚠️ — SIN USO claro
│   ├── departments.py            ⚠️ — SIN USO claro
│   ├── beds.py                  ⚠️ — SIN USO claro
│   ├── buildings.py              ⚠️ — SIN USO claro
│   ├── campuses.py               ⚠️ — SIN USO claro
│   ├── floors.py                ⚠️ — SIN USO claro
│   ├── hospitals.py              ⚠️ — SIN USO claro
│   ├── roles.py                  ⚠️ — SIN USO claro
│   ├── rooms.py                 ⚠️ — SIN USO claro
│   ├── staff.py                 ⚠️ — SIN USO claro
│   ├── suppliers.py             ⚠️ — SIN USO claro
│   ├── teams.py                 ⚠️ — SIN USO claro
│   ├── units.py                 ⚠️ — SIN USO claro
│   ├── warehouses.py             ⚠️ — SIN USO claro
│   ├── spare_parts.py            ⚠️ — SIN USO claro
│   └── purchase_orders.py        ⚠️ — SIN USO claro
│
├── schemas/                       ✅ EN PRODUCCIÓN (19 .py)
├── services/                      ⚠️ PARCIAL
│   ├── admin/
│   ├── audit/
│   ├── compliance/
│   └── tenant/
│
├── tasks/                          ⚠️ PARCIAL
│   ├── celery_app.py             ⚠️ — Celery configured but not active
│   ├── device_tasks.py           ⚠️ — ¿ejecutado?
│   ├── knowledge_tasks.py         ⚠️ — ¿ejecutado?
│   └── outbox_tasks.py           ⚠️ — ¿ejecutado?
│
├── events/                        ❌ DEAD CODE — duplicado de infrastructure/events.py
│   ├── publisher.py              ❌ — mismo que infrastructure/events.py
│   └── outbox.py                ❌ — mismo que infrastructure/messaging/outbox.py
│
└── enterprise/                   ⚠️ PARCIAL
    ├── licensing.py              ⚠️ — ¿usado?
    ├── versioning.py              ⚠️ — ¿usado?
    └── support.py                ⚠️ — ¿usado?
```

---

## 4. DESGLOSE DETALLADO: core/

### 4.1 core/PHASE_1/

```
core/PHASE_1/
├── domain/                       ✅ IMPLEMENTADO — entidades reales
│   ├── device/                  ✅ device.py (AggregateRoot), value_objects, repository ABC
│   ├── incident/               ✅ EngineeringIncident (AggregateRoot)
│   ├── knowledge/               ✅ KnowledgeArticle (AggregateRoot)
│   ├── organization/            ✅ Organization aggregate
│   ├── asset/                   ✅ Asset aggregate
│   ├── capacity/                ✅ HospitalCapacity aggregate
│   ├── department/              ⚠️ PARCIAL
│   ├── inventory/              ⚠️ PARCIAL
│   ├── staffing/              ⚠️ PARCIAL
│   └── models/                 ⚠️ Shared domain models
│
├── infrastructure/               ⚠️ PARCIAL — MEZCLA de conceptos
│   ├── container/               ❌ DEAD CODE — 19 archivos, nunca usado por apps/
│   ├── boot/                   ❌ DEAD CODE — usado solo por PHASE_2/runtime (dead)
│   ├── lifecycle/              ❌ DEAD CODE — mismo
│   ├── diagnostics/            ❌ DEAD CODE — mismo
│   ├── diagnostic/             ❌ DEAD CODE — carpeta vacía
│   ├── events/                ⚠️ PARCIAL — EventBus, pero PHASE_2 lo importa
│   ├── contracts/             ✅ ACTIVO — AuthenticationProvider, AuditProvider, etc.
│   │   ├── security/          ✅ USADO por apps/api middleware
│   │   ├── cognitive/         ⚠️ PARCIAL
│   │   ├── workflow.py        ⚠️ PARCIAL
│   │   ├── knowledge.py       ⚠️ PARCIAL
│   │   ├── reasoning.py       ⚠️ PARCIAL
│   │   ├── tool.py           ⚠️ PARCIAL
│   │   ├── memory.py         ⚠️ PARCIAL
│   │   ├── planner.py        ⚠️ PARCIAL
│   │   ├── provider.py        ⚠️ PARCIAL
│   │   ├── base.py           ⚠️ PARCIAL
│   │   └── diagnostic.py     ⚠️ PARCIAL
│   ├── shared/                ✅ ACTIVO — ValueObjects, Result, primitives compartidos
│   │   ├── primitives/       ✅ USADO por TODO
│   │   ├── value_objects/   ✅ USADO por TODO
│   │   ├── entities/         ✅ USADO por TODO
│   │   ├── errors/           ✅ USADO
│   │   └── events/          ✅ USADO (domain events)
│   └── biomedical/           ⚠️ PARCIAL
│       ├── clinical_context/
│       ├── decision_support/
│       ├── device_platform/
│       └── hospital_twin/
│
├── clinical/                    ⚠️ PARCIAL
│   └── clinical/
│       ├── cdss/
│       ├── diagnosis/
│       ├── predictive/
│       └── troubleshooting/
│
└── workflows/                   ⚠️ PARCIAL
    ├── composition/
    ├── workflow/
    └── workflows/
```

### 4.2 core/PHASE_2/ — AI Kernel

```
core/PHASE_2/
├── ai/                          ⚠️ PARCIAL — 19 subdirectorios
│   ├── kernel/                  ⚠️ PARCIAL
│   ├── memory/                  ⚠️ PARCIAL
│   ├── rag/                    ⚠️ PARCIAL
│   ├── cognitive/               ⚠️ PARCIAL
│   │   ├── memory/            ⚠️ DUPLICADO — ¿duplica ai/memory?
│   │   ├── rag/              ⚠️ DUPLICADO — ¿duplica ai/rag?
│   │   ├── reasoning/         ⚠️ DUPLICADO — ¿duplica reasoning/?
│   │   ├── conversation/
│   │   ├── context/
│   │   ├── safety/
│   │   └── tools/
│   ├── providers/              ⚠️ PARCIAL
│   ├── contracts/              ⚠️ PARCIAL
│   ├── dto/
│   ├── domain/
│   ├── exceptions/
│   ├── interfaces/
│   ├── prompt/
│   ├── registry/
│   ├── response/
│   ├── sessions/
│   ├── tools/
│   ├── context/
│   ├── context_builder/
│   ├── integration/
│   ├── di/                     ❌ DEAD CODE — solo __init__.py vacío
│   └── __init__.py
│
├── embeddings/                  ⚠️ PARCIAL
├── retrieval/                   ⚠️ PARCIAL
├── reasoning/                  ⚠️ PARCIAL
├── planner/                   ⚠️ PARCIAL
├── orchestration/               ⚠️ PARCIAL
├── orchestrator/               ⚠️ PARCIAL — ¿DUPLICADO de orchestration/?
├── session/                   ⚠️ PARCIAL
├── execution/                  ⚠️ PARCIAL
├── ingestion/                  ⚠️ PARCIAL
├── intent/                    ⚠️ PARCIAL
├── learning/                  ⚠️ PARCIAL
├── decision/                  ⚠️ PARCIAL
├── router/                    ⚠️ PARCIAL
├── scheduler/                  ⚠️ PARCIAL
├── pipeline/                   ⚠️ PARCIAL
├── planning/                   ⚠️ PARCIAL
├── providers/                 ⚠️ PARCIAL
│   └── providers/              ⚠️ DUPLICADO — ¿duplica ai/providers/?
├── plugins/                    ⚠️ PARCIAL
├── registry/                   ⚠️ PARCIAL
├── sdk/                       ⚠️ PARCIAL
├── capabilities/               ⚠️ PARCIAL
├── runtime/                   ❌ DEAD CODE — nunca usado fuera de sí mismo
├── cognitive/runtime.py        ⚠️ PARCIAL — ¿diferente de runtime/?
├── agents/                    ⚠️ PARCIAL
├── context/engine/             ⚠️ PARCIAL
└── context/engine/_internal/  ⚠️ PARCIAL
```

### 4.3 core/PHASE_3/

```
core/PHASE_3/
├── intelligence/               ⚠️ PARCIAL
│   ├── confidence/
│   ├── decision/
│   ├── evidence/
│   ├── explainability/
│   ├── foundation/             ✅ USADO por PHASE_4
│   │   └── enums.py           ✅ — EvidenceLevel importado por PHASE_4
│   ├── improvement/
│   ├── knowledge/
│   ├── learning/
│   ├── reasoning/              ⚠️ PARCIAL — PHASE_4 lo importa
│   ├── rules/
│   ├── safety/
│   └── validation/
├── recommendation/             ✅ IMPLEMENTADO — usado por apps/api
│   ├── domain/
│   │   ├── entities/         ✅ AIRecommendation aggregate
│   │   ├── repositories/     ✅ RecommendationRepository ABC
│   │   ├── value_objects/
│   │   └── services/
│   └── integrations/
├── integrations/
└── knowledge_assets/
```

### 4.4 core/PHASE_4/

```
core/PHASE_4/
├── epic10_sync_engine/         ⚠️ PARCIAL
├── epic11_governance/         ⚠️ PARCIAL
├── epic1_document_processing/  ⚠️ PARCIAL
├── epic2_knowledge_extraction/ ⚠️ PARCIAL
├── epic3_clinical_embeddings/ ⚠️ PARCIAL
├── epic4_vector_indexing/     ⚠️ PARCIAL
├── epic5_hybrid_retrieval/   ⚠️ PARCIAL
├── epic6_clinical_rag/       ⚠️ PARCIAL
├── epic7_citation_traceability/ ⚠️ PARCIAL
├── epic8_knowledge_quality/  ⚠️ PARCIAL
├── epic9_knowledge_repository/ ⚠️ PARCIAL
└── foundation/               ⚠️ PROBLEMA — imports infraestructura de PHASE_2
    ├── __init__.py            ⚠️ — 20+ imports de otros PHASEs (domain + infra)
    ├── config/
    ├── constants/
    ├── events/
    ├── exceptions/
    └── __init__.py
```

### 4.5 core/PHASE_5/ — Multi-Agent

```
core/PHASE_5/
├── epic4_knowledge_agent/      ⚠️ SCAFFOLDING
├── epic5_rag_agent/           ⚠️ SCAFFOLDING
├── epic6_diagnostic_agent/    ⚠️ SCAFFOLDING
├── epic7_collaboration/       ⚠️ SCAFFOLDING
├── epic8_consensus/          ⚠️ SCAFFOLDING
├── epic9_memory/              ⚠️ SCAFFOLDING
└── foundation/               ⚠️ PROBLEMA — 5 imports comentados
    ├── contracts/             ⚠️ — Gateway contracts definidos
    ├── domain/               ⚠️
    ├── events/               ⚠️
    ├── gateways/             ❌ SIN INTEGRAR — 5 imports comentados
    ├── lifecycle/
    ├── messaging/
    ├── registry/
    ├── types/
    └── context/
```

### 4.6 core/PHASE_7/

```
core/PHASE_7/
├── admin/                     ⚠️ PARCIAL
│   ├── api/
│   ├── domain/
│   └── services/
├── audit/                     ⚠️ PARCIAL
│   ├── api/
│   ├── compliance/
│   ├── dashboard/
│   ├── logger/
│   └── repository/
├── compliance/                 ⚠️ PARCIAL
│   ├── fda/
│   ├── hipaa/
│   ├── iec_62304/
│   ├── iso_13485/
│   └── security/
├── infrastructure/            ⚠️ PLATAFORMA — no dominio
│   ├── deployment/
│   │   ├── ci_cd/
│   │   └── docker/
│   ├── ha/
│   ├── recovery/
│   └── scaling/
├── observability/             ⚠️ PLATAFORMA
│   ├── alerts/
│   ├── dashboards/
│   ├── logging/
│   ├── metrics/
│   └── tracing/
└── tenant/                   ⚠️ PARCIAL
    ├── api/
    ├── isolation/
    ├── manager/
    ├── migrations/
    └── quotas/
```

### 4.7 core/LEGACY/

```
core/LEGACY/
├── collaboration/              ❌ DEAD CODE
│   ├── resolver.py
│   ├── sessions.py
│   ├── consensus.py
│   ├── aggregator.py
│   ├── types.py
│   ├── communication_bus.py
│   ├── dispatcher.py
│   ├── events.py
│   ├── engine.py
│   ├── messaging.py
│   ├── protocol.py
│   ├── shared_context.py
│   └── __init__.py
└── tools/                    ❌ DEAD CODE
    ├── catalog/
    ├── exceptions.py
    ├── models.py
    ├── validation.py
    ├── interfaces.py
    ├── execution.py
    ├── tool_registry.py
    ├── tool_pipeline.py
    └── __init__.py
```

**Evidence:** `grep -rn "from core.LEGACY" core/ apps/ --include="*.py"` → vacío fuera de `core/LEGACY/`

---

## 5. DESGLOSE DETALLADO: packages/

```
packages/
├── sdk/src/index.ts           ❌ STUB — 1 línea, nunca usado
├── schemas/src/index.ts       ❌ STUB — 1 línea, nunca usado
├── prompts/src/index.ts       ❌ STUB — 1 línea, nunca usado
└── shared/src/index.ts       ❌ STUB — 1 línea, nunca usado
```

**Evidence:** Ningún archivo de apps/web importa de packages/. El frontend usa Supabase directo.

---

## 6. DESGLOSE DETALLADO: infra/

```
infra/
├── k8s/
│   ├── deployment.yaml        ✅ EN PRODUCCIÓN
│   ├── service.yaml           ✅ EN PRODUCCIÓN
│   ├── configmap.yaml        ✅ EN PRODUCCIÓN
│   ├── namespace.yaml        ✅ EN PRODUCCIÓN
│   └── grafana-alerts.yaml  ⚠️ PARCIAL
│
├── helm/eren-api/            ✅ EN PRODUCCIÓN
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       └── ingress.yaml
│
├── production/                ⚠️ PARCIAL
│   ├── __init__.py
│   ├── alerting.py           ⚠️ — ¿conectado a K8s?
│   ├── backup.py            ⚠️
│   ├── cache.py             ⚠️
│   ├── monitoring.py        ⚠️
│   └── security.py          ⚠️
│
└── scripts/
    ├── backup.sh             ⚠️ — ¿probado?
    ├── deploy.sh             ⚠️ — ¿probado?
    └── rollback.sh           ⚠️ — ¿probado?
```

---

## 7. LÍNEAS DE CÓDIGO ESTIMADAS

| Área | Archivos .py | Líneas estimadas | Estado arquitectura |
|---|---|---|---|
| core/PHASE_1 | 1,154 | ~90,000 | ⚠️ PARCIAL |
| core/PHASE_2 | ~600 | ~50,000 | ⚠️ PARCIAL |
| core/PHASE_3 | ~200 | ~15,000 | ⚠️ PARCIAL |
| core/PHASE_4 | ~150 | ~12,000 | ⚠️ PARCIAL |
| core/PHASE_5 | ~200 | ~15,000 | ⚠️ SCAFFOLDING |
| core/PHASE_7 | ~150 | ~12,000 | ⚠️ PARCIAL |
| core/LEGACY | ~20 | ~2,000 | ❌ DEAD |
| apps/api | 180 | ~15,000 | ✅ EN PRODUCCIÓN |
| tests (total) | ~211 | ~20,000 | ⚠️ PARCIAL |
| **Total Python** | **~2,865** | **~231,000** | — |

---

## 8. DEPENDENCIAS EXTERNAS

### Python (apps/api/pyproject.toml)

| Paquete | Propósito | Estado uso |
|---|---|---|
| fastapi | Web framework | ✅ ACTIVO |
| uvicorn | ASGI server | ✅ ACTIVO |
| pydantic | Validation | ✅ ACTIVO |
| sqlalchemy | ORM | ✅ ACTIVO |
| alembic | Migrations | ✅ ACTIVO |
| supabase | Auth + DB | ✅ ACTIVO |
| redis | Cache | ✅ ACTIVO |
| aio-pika | RabbitMQ | ✅ ACTIVO |
| opentelemetry | Observability | ⚠️ PARCIAL |
| celery | Background tasks | ⚠️ CONFIGURED |
| httpx | HTTP client | ✅ ACTIVO |
| hvac | Vault | ⚠️ STUB |

### TypeScript (apps/web/package.json)

| Paquete | Propósito | Estado uso |
|---|---|---|
| @supabase/ssr | SSR auth | ✅ ACTIVO |
| @supabase/supabase-js | Client | ✅ ACTIVO |
| next 16 | Framework | ✅ ACTIVO |
| react 19 | UI | ✅ ACTIVO |
| @tanstack/react-query | Data fetching | ⚠️ PARCIAL |
| zustand | State | ⚠️ PARCIAL |
| recharts | Charts | ⚠️ PARCIAL |

---

## 9. RESUMEN DE ENTRADAS DE USUARIO

| Entry point | Estado | Arquitectura | Entry real |
|---|---|---|---|
| FastAPI (apps/api) | ✅ EN PRODUCCIÓN | API REST | ✅ |
| Next.js (apps/web) | ✅ EN PRODUCCIÓN | SPA + SSR | ✅ |
| CLI | ❌ NO EXISTE | — | — |
| Desktop | ❌ STUB | — | — |
| Mobile | ❌ STUB | — | — |
| Voice | ❌ NO EXISTE | — | — |
| Workers | ⚠️ CONFIGURED | Celery | ⚠️ |
| Agents | ❌ NO EXISTE | — | — |

---

*Inventario generado: 2026-08-03*
