# PROJECT TREE — Árbol Completo del Proyecto

**Fecha:** 2026-08-03

```
EREN/
│
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py                    ✅ EN PRODUCCIÓN
│   │   │   ├── __init__.py
│   │   │   ├── api/                      ✅ EN PRODUCCIÓN (6 submódulos)
│   │   │   │   ├── v1/admin/
│   │   │   │   ├── v1/audit/
│   │   │   │   ├── v1/compliance/
│   │   │   │   ├── v1/tenants/
│   │   │   │   └── v1/users/
│   │   │   ├── config/
│   │   │   ├── core/                    ✅ EN PRODUCCIÓN
│   │   │   │   ├── database.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── logging.py
│   │   │   │   ├── config/
│   │   │   │   └── security/
│   │   │   ├── domain/                 ✅ EN PRODUCCIÓN (17 submódulos)
│   │   │   │   ├── device/
│   │   │   │   │   ├── repository.py    ✅ 2 clases: Protocol + SQLAlchemy
│   │   │   │   │   ├── service.py       ✅
│   │   │   │   │   ├── events.py        ✅
│   │   │   │   │   ├── cache.py         ✅
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── incident/
│   │   │   │   ├── work_order/
│   │   │   │   │   ├── repository.py
│   │   │   │   │   ├── service.py
│   │   │   │   │   ├── events.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── recommendation/
│   │   │   │   ├── knowledge/
│   │   │   │   ├── department/       ⚠️ SIN USO
│   │   │   │   ├── inventory/        ⚠️ SIN USO
│   │   │   │   ├── organization/     ⚠️ SIN USO
│   │   │   │   ├── staffing/         ⚠️ SIN USO
│   │   │   │   ├── capacity/         ⚠️ SIN USO
│   │   │   │   ├── asset/            ⚠️ SIN USO
│   │   │   │   └── __init__.py
│   │   │   ├── infrastructure/      ⚠️ PARCIAL
│   │   │   │   ├── repositories/    ✅ 4 archivos + __init__
│   │   │   │   ├── messaging/       ✅ rabbitmq + outbox + cache
│   │   │   │   ├── models/         ✅ 13 SQLAlchemy models
│   │   │   │   ├── observability/   ✅ logging + tracing
│   │   │   │   ├── events.py       ⚠️ DUPLICADO
│   │   │   │   ├── vault/          ❌ STUB
│   │   │   │   └── unit_of_work.py ❌ DEAD CODE
│   │   │   ├── integrations/      ❌ 4 STUBS SIN USO
│   │   │   ├── middleware/        ✅ EN PRODUCCIÓN (4 archivos)
│   │   │   ├── models/           ⚠️ DUPLICADO de infrastructure/models/
│   │   │   ├── providers/        ⚠️ PARCIAL
│   │   │   │   ├── circuit_breaker.py ❌ DEAD CODE
│   │   │   │   └── security/supabase_auth.py ✅
│   │   │   ├── routers/           ✅ EN PRODUCCIÓN (22 routers)
│   │   │   │   ├── __init__.py   ✅ api_router
│   │   │   │   ├── devices.py    ✅
│   │   │   │   ├── work_orders.py ✅
│   │   │   │   ├── health.py     ✅
│   │   │   │   ├── auth.py       ✅
│   │   │   │   └── 18 routers más ⚠️ 14 SIN USO claro
│   │   │   ├── schemas/         ✅ EN PRODUCCIÓN (19 archivos)
│   │   │   ├── services/        ⚠️ PARCIAL
│   │   │   │   ├── admin/
│   │   │   │   ├── audit/
│   │   │   │   ├── compliance/
│   │   │   │   └── tenant/
│   │   │   ├── tasks/          ⚠️ PARCIAL (Celery)
│   │   │   │   ├── celery_app.py
│   │   │   │   ├── device_tasks.py
│   │   │   │   ├── knowledge_tasks.py
│   │   │   │   └── outbox_tasks.py
│   │   │   ├── events/        ❌ DEAD CODE — duplicado de infrastructure/
│   │   │   │   ├── publisher.py
│   │   │   │   └── outbox.py
│   │   │   └── enterprise/    ❌ DEAD CODE
│   │   │       ├── licensing.py
│   │   │       ├── versioning.py
│   │   │       └── support.py
│   │   ├── migrations/         ✅ EN PRODUCCIÓN (8 archivos)
│   │   ├── scripts/           ⚠️ PARCIAL
│   │   │   ├── migrate.py
│   │   │   └── run_outbox_worker.py
│   │   └── tests/            ⚠️ PARCIAL
│   │       ├── unit/         (12 archivos)
│   │       ├── integration/   (3 archivos)
│   │       ├── conftest.py
│   │       └── test_health.py
│   ├── pyproject.toml        ✅
│   ├── uv.lock               ✅
│   ├── Dockerfile            ✅
│   ├── README.md             ✅
│   └── migrations/
│
│   ├── web/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── (auth)/login/
│   │   │   │   └── (dashboard)/    ✅ 14 páginas
│   │   │   │       ├── dashboard/
│   │   │   │       ├── ai/
│   │   │   │       ├── equipos/
│   │   │   │       ├── establecimientos/
│   │   │   │       ├── knowledge/
│   │   │   │       ├── kpis/
│   │   │   │       ├── mantenimientos/
│   │   │   │       ├── administration/
│   │   │   │       ├── analytics/
│   │   │   │       ├── operations/
│   │   │   │       ├── reports/
│   │   │   │       ├── notifications/
│   │   │   │       ├── connectors/
│   │   │   │       └── workspace/
│   │   │   ├── components/     ✅ 30+ componentes
│   │   │   │   ├── auth/AuthProvider.tsx ⚠️ Supabase directo
│   │   │   │   └── ui/        ✅ 6 componentes base
│   │   │   ├── modules/       ✅ 12 módulos
│   │   │   │   ├── dashboard/
│   │   │   │   ├── ai/
│   │   │   │   ├── equipos/    ⚠️ 1 service
│   │   │   │   ├── establecimientos/
│   │   │   │   ├── mantenimientos/
│   │   │   │   ├── kpis/
│   │   │   │   ├── administration/
│   │   │   │   ├── analytics/
│   │   │   │   ├── operations/
│   │   │   │   ├── reports/
│   │   │   │   ├── notifications/
│   │   │   │   ├── connectors/
│   │   │   │   ├── knowledge/
│   │   │   │   ├── workspace/
│   │   │   │   └── shared/
│   │   │   ├── hooks/         ✅ 15 hooks
│   │   │   ├── lib/          ⚠️ PROBLEMA
│   │   │   │   ├── supabase.ts   ⚠️ 20 Supabase directos
│   │   │   │   ├── queries.ts    ⚠️ 4 queries directas
│   │   │   │   ├── storage.ts   ⚠️ 3 uploads directos
│   │   │   │   └── kpis.ts
│   │   │   └── api/create-user/
│   │   ├── tests/            ⚠️ PARCIAL (8 tests)
│   │   │   ├── unit/
│   │   │   └── web/modules/
│   │   ├── middleware.ts     ✅
│   │   ├── next.config.ts   ✅
│   │   └── package.json     ✅
│   │
│   ├── desktop/              ❌ STUB (1 archivo)
│   └── mobile/              ❌ STUB (1 archivo)
│
├── core/
│   ├── PHASE_1/             ⚠️ PARCIAL (1,154 .py)
│   │   ├── domain/
│   │   │   ├── device/     ✅ AggregateRoot + 7 VOs + Repository ABC
│   │   │   ├── incident/   ✅ AggregateRoot
│   │   │   ├── knowledge/  ✅ AggregateRoot
│   │   │   ├── organization/ ✅ Aggregate
│   │   │   ├── asset/      ✅ Aggregate
│   │   │   ├── capacity/  ✅ Aggregate
│   │   │   ├── department/ ⚠️ PARCIAL
│   │   │   ├── inventory/  ⚠️ PARCIAL
│   │   │   ├── staffing/   ⚠️ PARCIAL
│   │   │   └── models/    ⚠️ PARCIAL
│   │   └── infrastructure/
│   │       ├── container/  ❌ DEAD CODE (19 archivos)
│   │       ├── boot/      ❌ DEAD CODE (~8 archivos)
│   │       ├── lifecycle/  ❌ DEAD CODE (~6 archivos)
│   │       ├── diagnostics/ ❌ DEAD CODE (19 archivos)
│   │       ├── diagnostic/ ❌ DEAD CODE (vacío)
│   │       ├── events/    ⚠️ PARCIAL
│   │       ├── contracts/  ✅ ACTIVO (21 archivos)
│   │       ├── shared/    ✅ ACTIVO
│   │       └── biomedical/ ⚠️ PARCIAL
│   │
│   ├── PHASE_2/             ⚠️ PARCIAL (~600 .py)
│   │   ├── ai/            ⚠️ PARCIAL (19 subdirectorios)
│   │   │   ├── kernel/
│   │   │   ├── memory/    ⚠️ PARCIAL
│   │   │   ├── rag/       ⚠️ PARCIAL
│   │   │   ├── cognitive/  ⚠️ PARCIAL
│   │   │   │   ├── memory/ ⚠️ DUPLICADO
│   │   │   │   ├── rag/   ⚠️ DUPLICADO
│   │   │   │   └── reasoning/ ⚠️ DUPLICADO
│   │   │   ├── providers/
│   │   │   ├── contracts/
│   │   │   ├── di/        ❌ DEAD CODE (vacío)
│   │   │   └── 12 más
│   │   ├── embeddings/    ⚠️ PARCIAL
│   │   ├── retrieval/     ⚠️ PARCIAL
│   │   ├── reasoning/     ⚠️ PARCIAL
│   │   ├── planner/      ⚠️ PARCIAL
│   │   ├── orchestration/ ⚠️ PARCIAL
│   │   ├── orchestrator/  ⚠️ DUPLICADO
│   │   ├── session/     ⚠️ PARCIAL
│   │   ├── execution/   ⚠️ PARCIAL
│   │   ├── runtime/     ❌ DEAD CODE (~15 archivos)
│   │   ├── agents/
│   │   ├── cognitive/runtime.py ⚠️ PARCIAL
│   │   └── 20+ más carpetas
│   │
│   ├── PHASE_3/             ⚠️ PARCIAL (~200 .py)
│   │   ├── intelligence/  ⚠️ PARCIAL (10 subdirectorios)
│   │   └── recommendation/ ✅ IMPLEMENTADO
│   │       ├── domain/
│   │       │   ├── entities/ ✅ AIRecommendation
│   │       │   ├── repositories/ ✅ ABC
│   │       │   ├── value_objects/
│   │       │   └── services/
│   │       └── integrations/
│   │
│   ├── PHASE_4/             ⚠️ PARCIAL (~150 .py)
│   │   ├── epic* folders   ⚠️ 9 epic folders
│   │   └── foundation/     ⚠️ IMPORTS PROBLEMÁTICOS
│   │
│   ├── PHASE_5/             ⚠️ SCAFFOLDING (~200 .py)
│   │   ├── epic*_agent/  ⚠️ 6 epic agents
│   │   └── foundation/
│   │       ├── contracts/
│   │       ├── gateways/   ❌ NO INTEGRADO (5 imports comentados)
│   │       └── domain/
│   │
│   ├── PHASE_7/             ⚠️ PARCIAL (~150 .py)
│   │   ├── admin/
│   │   ├── audit/
│   │   ├── compliance/
│   │   ├── infrastructure/ ⚠️ PLATAFORMA (no dominio)
│   │   │   ├── deployment/
│   │   │   ├── ha/
│   │   │   ├── recovery/
│   │   │   └── scaling/
│   │   ├── observability/ ⚠️ PLATAFORMA
│   │   │   ├── alerts/
│   │   │   ├── dashboards/
│   │   │   ├── logging/
│   │   │   ├── metrics/
│   │   │   └── tracing/
│   │   └── tenant/
│   │
│   ├── PHASE_6/             ❌ VACÍO
│   └── LEGACY/              ❌ DEAD CODE (~20 .py)
│       ├── collaboration/
│       └── tools/
│
├── packages/                ❌ 4 STUBS VACÍOS
│   ├── sdk/src/index.ts
│   ├── schemas/src/index.ts
│   ├── prompts/src/index.ts
│   └── shared/src/index.ts
│
├── tests/                  ⚠️ PARCIAL (~211 .py)
│   ├── unit/
│   │   ├── PHASE_1/     ⚠️ PARCIAL (~30)
│   │   ├── PHASE_2/    ⚠️ PARCIAL (~50)
│   │   ├── PHASE_3/    ⚠️ PARCIAL (~20)
│   │   ├── PHASE_4/    ⚠️ PARCIAL (~20)
│   │   ├── PHASE_5/    ⚠️ PARCIAL (~10)
│   │   ├── PHASE_7/    ⚠️ PARCIAL (~20)
│   │   ├── LEGACY/     ❌ DEAD (2)
│   │   └── plugins/    ⚠️ PARCIAL (3)
│   ├── integration/
│   │   ├── ai_core/
│   │   └── core/diagnostics/
│   ├── ai_core/        ⚠️ PARCIAL (2)
│   └── runtime/         ❌ DEAD (2)
│
├── docs/                   690 .md
│   ├── audit/            ✅ NUEVA CARPETA
│   ├── adr/              ⚠️ 12 archivos
│   ├── phases/           ⚠️ 492 archivos (epics + adrs)
│   ├── architecture/     ⚠️ 48 archivos
│   ├── roadmap/          ⚠️ 3 archivos
│   ├── guides/           ⚠️ 3 archivos
│   └── _archive/        ⚠️ ~50 obsoletos
│
├── infra/                  ✅ PARCIAL
│   ├── k8s/             ✅ 5 archivos
│   ├── helm/eren-api/   ✅ Helm chart completo
│   ├── production/      ⚠️ 6 archivos Python
│   └── scripts/         ⚠️ 3 bash scripts
│
├── .github/workflows/
│   └── ci.yml           ⚠️ Falta job de tests
│
├── docker-compose.yml    ⚠️ Falta RabbitMQ
├── pyproject.toml       ✅
├── package.json         ✅
└── pytest.ini            ✅
```

---

## CONTEOS POR ESTADO

```
✅ EN PRODUCCIÓN:       ~30 módulos/archivos
⚠️ PARCIAL:            ~80 módulos/archivos  
❌ DEAD CODE:           ~117 módulos/archivos
❌ STUB VACÍO:          ~20 módulos/archivos
⚠️ SIN USO:             ~30 módulos/archivos
⚠️ DUPLICADO:           ~10 módulos/archivos
```

---

*Árbol generado: 2026-08-03*
