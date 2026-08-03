# MATRIX — Elemento × Estado × Responsable

**Fecha:** 2026-08-03
**Filas:** ~200 elementos | **Ver también:** CORRECTION_LIST.md para lista priorizada

---

## CÓDIGO: apps/api/

| Elemento | Ubicación | Estado | Responsable | Usado por | Puede eliminarse | Riesgo |
|---|---|---|---|---|---|---|
| main.py | apps/api/app/ | ✅ EN PRODUCCIÓN | Backend | Todos | No | 🔴 |
| routers/__init__.py | apps/api/app/routers/ | ✅ EN PRODUCCIÓN | Backend | main.py | No | 🔴 |
| routers/devices.py | apps/api/app/routers/ | ✅ EN PRODUCCIÓN | Backend | routers/__init__ | No | 🔴 |
| routers/work_orders.py | apps/api/app/routers/ | ✅ EN PRODUCCIÓN | Backend | routers/__init__ | No | 🔴 |
| routers/health.py | apps/api/app/routers/ | ✅ EN PRODUCCIÓN | Backend | routers/__init__ | No | 🟡 |
| routers/auth.py | apps/api/app/routers/ | ✅ EN PRODUCCIÓN | Backend | routers/__init__ | No | 🟡 |
| routers/incidents.py | apps/api/app/routers/ | ⚠️ SIN RUTA | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/diagnosis.py | apps/api/app/routers/ | ⚠️ PARCIAL | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/patients.py | apps/api/app/routers/ | ⚠️ PARCIAL | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/organizations.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/departments.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/beds.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/buildings.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/campuses.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/floors.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/hospitals.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/roles.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/rooms.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/staff.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/suppliers.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/teams.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/units.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/warehouses.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/spare_parts.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| routers/purchase_orders.py | apps/api/app/routers/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| domain/device/service.py | apps/api/app/domain/ | ✅ EN PRODUCCIÓN | Backend | routers/devices.py | No | 🟡 |
| domain/device/repository.py | apps/api/app/domain/ | ✅ EN PRODUCCIÓN | Backend | service.py | No | 🟡 |
| domain/work_order/service.py | apps/api/app/domain/ | ✅ EN PRODUCCIÓN | Backend | routers/work_orders.py | No | 🟡 |
| domain/work_order/repository.py | apps/api/app/domain/ | ✅ EN PRODUCCIÓN | Backend | service.py | No | 🟡 |
| domain/incident/repository.py | apps/api/app/domain/ | ⚠️ SIN USO EN SERVICIO | Backend | ? | ⚠️ Investigar | 🟡 |
| domain/recommendation/repository.py | apps/api/app/domain/ | ✅ EN PRODUCCIÓN | Backend | ? | No | 🟡 |
| domain/knowledge/repository.py | apps/api/app/domain/ | ✅ EN PRODUCCIÓN | Backend | ? | No | 🟡 |
| domain/department/repository.py | apps/api/app/domain/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| domain/inventory/repository.py | apps/api/app/domain/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| domain/organization/repository.py | apps/api/app/domain/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| domain/staffing/repository.py | apps/api/app/domain/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| domain/capacity/repository.py | apps/api/app/domain/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| domain/asset/repository.py | apps/api/app/domain/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| infra/repositories/device.py | apps/api/app/infra/ | ✅ EN PRODUCCIÓN | Backend | routers/devices.py | No | 🟡 |
| infra/repositories/incident.py | apps/api/app/infra/ | ✅ EN PRODUCCIÓN | Backend | ? | No | 🟡 |
| infra/repositories/knowledge.py | apps/api/app/infra/ | ✅ EN PRODUCCIÓN | Backend | ? | No | 🟡 |
| infra/repositories/recommendation.py | apps/api/app/infra/ | ✅ EN PRODUCCIÓN | Backend | ? | No | 🟡 |
| infra/messaging/rabbitmq.py | apps/api/app/infra/ | ✅ CONNECTED | Backend | outbox.py | No | 🟡 |
| infra/messaging/outbox.py | apps/api/app/infra/ | ✅ CONNECTED | Backend | service.py | No | 🟡 |
| infra/messaging/cache.py | apps/api/app/infra/ | ✅ CONNECTED | Backend | routers/devices.py | No | 🟡 |
| infra/models/*.py | apps/api/app/infra/ | ✅ EN PRODUCCIÓN | Backend | repositories | No | 🟡 |
| infra/observability/logging.py | apps/api/app/infra/ | ✅ EN PRODUCCIÓN | Backend | main.py | No | 🟡 |
| infra/observability/tracing.py | apps/api/app/infra/ | ⚠️ PARCIAL | Backend | main.py | No | 🟡 |
| infra/events.py | apps/api/app/infra/ | ⚠️ PARCIAL | Backend | service.py | ⚠️ Duplicado | 🟡 |
| infra/unit_of_work.py | apps/api/app/infra/ | ❌ DEAD CODE | — | Nadie | **SÍ — eliminar** | 🟢 |
| infra/vault/client.py | apps/api/app/infra/ | ❌ STUB | — | Nadie | **SÍ — eliminar** | 🟢 |
| providers/circuit_breaker.py | apps/api/app/ | ❌ DEAD CODE | — | Nadie | **SÍ — eliminar** | 🟢 |
| providers/security/supabase_auth.py | apps/api/app/ | ✅ EN PRODUCCIÓN | Backend | middleware | No | 🟡 |
| integrations/mqtt_client.py | apps/api/app/ | ❌ STUB | — | Nadie | **SÍ — eliminar** | 🟢 |
| integrations/dicom_client.py | apps/api/app/ | ❌ STUB | — | Nadie | **SÍ — eliminar** | 🟢 |
| integrations/hl7_listener.py | apps/api/app/ | ❌ STUB | — | Nadie | **SÍ — eliminar** | 🟢 |
| integrations/fhir_client.py | apps/api/app/ | ❌ STUB | — | Nadie | **SÍ — eliminar** | 🟢 |
| enterprise/licensing.py | apps/api/app/ | ❌ DEAD CODE | — | Nadie | **SÍ — eliminar** | 🟢 |
| enterprise/versioning.py | apps/api/app/ | ❌ DEAD CODE | — | Nadie | **SÍ — eliminar** | 🟢 |
| enterprise/support.py | apps/api/app/ | ❌ DEAD CODE | — | Nadie | **SÍ — eliminar** | 🟢 |
| events/publisher.py | apps/api/app/ | ❌ DEAD CODE | — | Nadie | **SÍ — eliminar** | 🟢 |
| events/outbox.py | apps/api/app/ | ❌ DEAD CODE | — | Nadie | **SÍ — eliminar** | 🟢 |
| models/diagnosis.py | apps/api/app/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| models/patient.py | apps/api/app/ | ⚠️ SIN USO | Backend | ? | ⚠️ Investigar | 🟡 |
| tasks/celery_app.py | apps/api/app/ | ⚠️ PARCIAL | Backend | ? | ⚠️ Investigar | 🟡 |
| tasks/device_tasks.py | apps/api/app/ | ⚠️ PARCIAL | Backend | ? | ⚠️ Investigar | 🟡 |
| tasks/knowledge_tasks.py | apps/api/app/ | ⚠️ PARCIAL | Backend | ? | ⚠️ Investigar | 🟡 |
| tasks/outbox_tasks.py | apps/api/app/ | ⚠️ PARCIAL | Backend | ? | ⚠️ Investigar | 🟡 |

---

## CÓDIGO: core/PHASE_1/

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| domain/device/ | core/PHASE_1/domain/ | ✅ IMPLEMENTADO | No |
| domain/incident/ | core/PHASE_1/domain/ | ✅ IMPLEMENTADO | No |
| domain/knowledge/ | core/PHASE_1/domain/ | ✅ IMPLEMENTADO | No |
| domain/organization/ | core/PHASE_1/domain/ | ✅ IMPLEMENTADO | No |
| domain/asset/ | core/PHASE_1/domain/ | ✅ IMPLEMENTADO | No |
| domain/capacity/ | core/PHASE_1/domain/ | ⚠️ PARCIAL | No |
| domain/department/ | core/PHASE_1/domain/ | ⚠️ PARCIAL | No |
| domain/inventory/ | core/PHASE_1/domain/ | ⚠️ PARCIAL | No |
| domain/staffing/ | core/PHASE_1/domain/ | ⚠️ PARCIAL | No |
| domain/models/ | core/PHASE_1/domain/ | ⚠️ PARCIAL | No |
| infra/contracts/ | core/PHASE_1/infra/ | ✅ ACTIVO | No |
| infra/shared/ | core/PHASE_1/infra/ | ✅ ACTIVO | No |
| infra/events/ | core/PHASE_1/infra/ | ⚠️ PARCIAL | No |
| infra/container/ | core/PHASE_1/infra/ | ❌ DEAD CODE | **SÍ — eliminar** |
| infra/boot/ | core/PHASE_1/infra/ | ❌ DEAD CODE | **SÍ — eliminar** |
| infra/lifecycle/ | core/PHASE_1/infra/ | ❌ DEAD CODE | **SÍ — eliminar** |
| infra/diagnostics/ | core/PHASE_1/infra/ | ❌ DEAD CODE | **SÍ — eliminar** |
| infra/diagnostic/ | core/PHASE_1/infra/ | ❌ DEAD CODE | **SÍ — eliminar** |

---

## CÓDIGO: core/PHASE_2/

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| ai/kernel/ | core/PHASE_2/ai/ | ⚠️ PARCIAL | No |
| ai/memory/ | core/PHASE_2/ai/ | ⚠️ PARCIAL | No |
| ai/rag/ | core/PHASE_2/ai/ | ⚠️ PARCIAL | No |
| ai/cognitive/rag/ | core/PHASE_2/ai/ | ⚠️ DUPLICADO | ⚠️ Investigar |
| ai/cognitive/memory/ | core/PHASE_2/ai/ | ⚠️ DUPLICADO | ⚠️ Investigar |
| ai/providers/ | core/PHASE_2/ai/ | ⚠️ PARCIAL | No |
| ai/contracts/ | core/PHASE_2/ai/ | ⚠️ PARCIAL | No |
| ai/di/ | core/PHASE_2/ai/ | ❌ DEAD CODE | **SÍ — eliminar** |
| runtime/ | core/PHASE_2/ | ❌ DEAD CODE | **SÍ — eliminar** |
| embeddings/ | core/PHASE_2/ | ⚠️ PARCIAL | No |
| reasoning/ | core/PHASE_2/ | ⚠️ PARCIAL | No |
| retrieval/ | core/PHASE_2/ | ⚠️ PARCIAL | No |
| planner/ | core/PHASE_2/ | ⚠️ PARCIAL | No |
| orchestration/ | core/PHASE_2/ | ⚠️ PARCIAL | No |
| orchestrator/ | core/PHASE_2/ | ⚠️ DUPLICADO | ⚠️ Investigar |

---

## CÓDIGO: core/PHASE_3/

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| recommendation/ | core/PHASE_3/ | ✅ IMPLEMENTADO | No |
| intelligence/foundation/ | core/PHASE_3/ | ✅ USADO POR PHASE_4 | No |
| intelligence/reasoning/ | core/PHASE_3/ | ⚠️ PARCIAL | No |

---

## CÓDIGO: core/PHASE_4/

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| epic* folders | core/PHASE_4/ | ⚠️ PARCIAL | No |
| foundation/ | core/PHASE_4/ | ⚠️ IMPORT PROBLEMÁTICO | No (corregir imports) |

---

## CÓDIGO: core/PHASE_5/

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| epic* agents | core/PHASE_5/ | ⚠️ SCAFFOLDING | No |
| foundation/contracts/ | core/PHASE_5/ | ⚠️ PARCIAL | No |
| foundation/gateways/ | core/PHASE_5/ | ⚠️ NO INTEGRADO | No (implementar) |

---

## CÓDIGO: core/LEGACY/

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| collaboration/ | core/LEGACY/ | ❌ DEAD CODE | **SÍ — eliminar** |
| tools/ | core/LEGACY/ | ❌ DEAD CODE | **SÍ — eliminar** |

---

## FRONTEND: apps/web/

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| lib/queries.ts | apps/web/src/lib/ | ⚠️ PROBLEMA | No (migrar a SDK) |
| lib/supabase.ts | apps/web/src/lib/ | ⚠️ PROBLEMA | No (migrar a SDK) |
| lib/storage.ts | apps/web/src/lib/ | ⚠️ PROBLEMA | No (migrar a SDK) |
| lib/kpis.ts | apps/web/src/lib/ | ⚠️ PARCIAL | No |
| modules/dashboard/ | apps/web/src/modules/ | ✅ EN PRODUCCIÓN | No |
| modules/ai/ | apps/web/src/modules/ | ⚠️ PARCIAL | No |
| modules/equipos/ | apps/web/src/modules/ | ✅ EN PRODUCCIÓN | No |
| modules/knowledge/ | apps/web/src/modules/ | ⚠️ PARCIAL | No |

---

## PACKAGES: packages/

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| sdk/ | packages/sdk/ | ❌ STUB VACÍO | **SÍ — eliminar o llenar** |
| schemas/ | packages/schemas/ | ❌ STUB VACÍO | **SÍ — eliminar o llenar** |
| prompts/ | packages/prompts/ | ❌ STUB VACÍO | **SÍ — eliminar o llenar** |
| shared/ | packages/shared/ | ❌ STUB VACÍO | **SÍ — eliminar o llenar** |

---

## CI/CD

| Elemento | Ubicación | Estado | Puede eliminarse |
|---|---|---|---|
| ci.yml | .github/workflows/ | ⚠️ FALTA TESTS | No (corregir) |
| ruff lint | ci.yml lint job | ⚠️ "|| true" ignora errores | No (corregir) |
| mypy typecheck | ci.yml typecheck job | ⚠️ no-strict mode | No (corregir) |
| docker-compose.yml | raíz | ✅ CONFIGURADO | No |
| infra/k8s/ | infra/ | ✅ CONFIGURADO | No |
| infra/helm/ | infra/ | ✅ CONFIGURADO | No |

---

*Matriz generada: 2026-08-03*
