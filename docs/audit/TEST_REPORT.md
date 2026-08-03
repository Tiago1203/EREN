# TEST REPORT — Estado de Tests en el Repositorio

**Fecha:** 2026-08-03

---

## 1. RESUMEN EJECUTIVO

| Área | Tests | Archivos | Estado |
|---|---|---|---|
| apps/api unit | ~12 | 12 .py | ⚠️ PARCIAL — algunos pasan, algunos fallan |
| apps/api integration | 3 | 3 .py | ⚠️ PARCIAL |
| apps/web unit | 8 | 8 .test.* | ⚠️ PARCIAL |
| core/unit PHASE_1 | ~30 | 30 .py | ⚠️ PARCIAL — collection errors |
| core/unit PHASE_2 | ~50 | 50 .py | ⚠️ PARCIAL — collection errors |
| core/unit PHASE_3 | ~20 | 20 .py | ⚠️ PARCIAL |
| core/unit PHASE_4 | ~20 | 20 .py | ⚠️ PARCIAL |
| core/unit PHASE_5 | ~10 | 10 .py | ⚠️ PARCIAL |
| core/unit PHASE_7 | ~20 | 20 .py | ⚠️ PARCIAL |
| core/unit LEGACY | 2 | 2 .py | ❌ DEAD — LEGACY es dead |
| core/integration | 5 | 5 .py | ⚠️ PARCIAL |
| core/ai_core | 2 | 2 .py | ⚠️ PARCIAL |
| core/runtime | 2 | 2 .py | ❌ DEAD — runtime es dead |
| **TOTAL** | **~211** | **~211** | **⚠️ PARCIAL** |

---

## 2. apps/api/tests/ — DETALLE

### 2.1 Unit Tests (apps/api/tests/unit/)

```
apps/api/tests/unit/
├── test_device_router.py       ⚠️ PARCIAL
├── test_device_service.py     ⚠️ PARCIAL
├── test_work_order_router.py  ⚠️ PARCIAL
├── test_work_order_service.py ⚠️ PARCIAL
├── test_recommendation_service.py ⚠️ PARCIAL
├── test_knowledge_service.py  ⚠️ PARCIAL
├── test_diagnosis_service.py  ⚠️ PARCIAL
├── test_diagnosis_service_negative.py ⚠️ PARCIAL
├── test_patient_service.py    ⚠️ PARCIAL
├── test_patient_service_negative.py ⚠️ PARCIAL
├── test_device_service.py      ⚠️ PARCIAL
└── __init__.py
```

**Hallazgo:** No existe `test_incident_router.py` ni `test_incident_service.py` a pesar de que `incident` es un dominio principal.

**Hallazgo:** Los tests de diagnosis, patient, y recommendation no parecen tener archivos de router dedicados en apps/api/app/routers/.

### 2.2 Integration Tests (apps/api/tests/integration/)

```
apps/api/tests/integration/
├── test_device_flow.py         ⚠️ PARCIAL
├── test_clinical_flow.py      ⚠️ PARCIAL
└── test_patient_flow.py      ⚠️ PARCIAL
```

**Hallazgo:** Solo 3 flujos de integración para cubrir el sistema completo. No hay test de:
- Flujo completo de work orders
- Flujo de eventos (Outbox → RabbitMQ)
- Flujo de authentication/authorization
- Flujo de multi-tenant

### 2.3 Test Health

```
apps/api/tests/test_health.py
```

**Hallazgo:** Solo 1 test de health. No verifica que los endpoints críticos respondan.

---

## 3. apps/web/tests/ — DETALLE

```
apps/web/tests/unit/
├── components/
│   └── KpiGrid.test.tsx       ⚠️ PARCIAL
├── services/
│   ├── analytics.service.test.ts
│   └── dashboard.service.test.ts
└── web/modules/
    ├── equipos/
    │   └── test_equipos_module.test.ts
    ├── establecimientos/
    │   └── test_establecimientos_module.test.ts
    ├── kpis/
    │   └── test_kpis_module.test.ts
    └── mantenimientos/
        └── test_mantenimientos_module.test.ts
```

**Hallazgo:** Tests para los 4 módulos principales. Faltan tests para:
- Module de AI (chat)
- Module de analytics avanzado
- Module de notifications
- Module de operations
- Module de workspace
- Module de reports
- Module de administration
- Module de knowledge
- Module de connectors
- Auth flow completo
- Storage flow

**Coverage estimado:** ~20% del frontend

---

## 4. core/tests/ — DETALLE

### 4.1 PHASE_1 Tests

```
tests/unit/PHASE_1/
├── domain/
│   ├── device/
│   │   └── test_device.py      ⚠️ PARCIAL
│   ├── incident/
│   │   └── test_incident.py    ⚠️ PARCIAL
│   ├── knowledge/
│   │   ├── test_knowledge.py
│   │   ├── test_knowledge_article.py
│   │   └── test_registry.py
│   └── models/
│       └── test_models.py
├── infrastructure/
│   ├── boot/
│   │   └── test_boot_manager.py ⚠️ PARCIAL — boot es dead
│   ├── container/
│   │   └── test_container.py  ⚠️ PARCIAL — container es dead
│   ├── diagnostics/
│   │   └── test_diagnostics.py ⚠️ PARCIAL — diagnostics es dead
│   ├── events/
│   │   └── test_events.py     ⚠️ PARCIAL
│   ├── lifecycle/
│   │   └── test_lifecycle.py  ⚠️ PARCIAL — lifecycle es dead
│   └── shared/
│       └── test_shared.py
└── workflows/
    ├── composition/
    │   └── test_composition.py
    └── workflows/
        └── test_workflows.py
```

**Hallazgo crítico:** Tests para infrastructure/boot, container, lifecycle, diagnostics — todo dead code. Los tests existen pero testean código que nadie usa.

### 4.2 PHASE_2 Tests

```
tests/unit/PHASE_2/
├── agents/
├── ai/
├── capabilities/
├── cognitive/
│   └── rag/
│       ├── domain/
│       │   ├── entities/
│       │   └── services/
│       └── test_*.py
├── context/
├── decision/
├── embeddings/
├── execution/
├── ingestion/
├── intent/
├── learning/
├── memory/
├── orchestration/
├── orchestrator/
├── pipeline/
├── planner/
├── planning/
├── plugins/
├── providers/
├── rag/
├── reasoning/
├── registry/
├── retrieval/
├── router/
├── runtime/
│   └── test_runtime.py        ❌ DEAD — runtime es dead
├── scheduler/
├── sdk/
├── session/
└── test_*.py
```

**Hallazgo:** ~50 archivos de tests cubriendo todo PHASE_2. Muchos de estos tests probablemente fallan porque PHASE_2 está en scaffolding.

### 4.3 PHASE_3-7 Tests

```
tests/unit/PHASE_3/        ~20 archivos
tests/unit/PHASE_4/        ~20 archivos
tests/unit/PHASE_5/        ~10 archivos
tests/unit/PHASE_7/        ~20 archivos
tests/unit/plugins/         ~3 archivos
```

---

## 5. CONTRACTS TESTS

**Hallazgo crítico:** **NO EXISTEN contract tests.**

Los contract tests verificarían que:
- `SQLAlchemyDeviceRepository` implementa correctamente el ABC `DeviceRepository` de `core/PHASE_1/`
- `SQLAlchemyIncidentRepository` implementa correctamente el ABC `IncidentRepository` de `core/PHASE_1/`
- Los adapters de PHASE_2, PHASE_4, PHASE_5 cumplen sus contratos

**ausencia de contract tests es la razón por la que los dos sistemas de puertos coexisten sin que se detecten incompatibilidades.**

---

## 6. COBERTURA

### apps/api

```
tool.coverage.run source = ["core"]
```

**Problema:** La cobertura solo mide `core/`, no `apps/api/app/`.

```
tool.coverage.report exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@abstractmethod",
]
```

**Hallazgo:** No hay cobertura reportada para apps/api/app/.

### core/

```
core/PHASE_1/      → tests/unit/PHASE_1/     ~30 tests
core/PHASE_2/      → tests/unit/PHASE_2/     ~50 tests
core/PHASE_3/      → tests/unit/PHASE_3/     ~20 tests
core/PHASE_4/      → tests/unit/PHASE_4/     ~20 tests
core/PHASE_5/      → tests/unit/PHASE_5/     ~10 tests
core/PHASE_7/      → tests/unit/PHASE_7/     ~20 tests
```

**Estimado de cobertura:** ~40-60% para PHASE_1, ~20-30% para PHASE_2, <20% para otros.

---

## 7. PROBLEMAS CONOCIDOS

### Problema 1: CI no corre tests automáticamente

```yaml
# .github/workflows/ci.yml
jobs:
  lint:
  typecheck:
  # ← NO HAY job "test"
```

**Evidencia:**
```bash
grep -n "pytest\|test" .github/workflows/ci.yml
# → vacío (no hay job de tests)
```

**Impacto:** Los tests pueden estar fallando y nadie se entera.

### Problema 2: Collection errors en tests de PHASE_1 y PHASE_2

Los tests de `core/PHASE_1/` y `core/PHASE_2/` probablemente tienen collection errors debido a imports faltantes o circulares.

### Problema 3: Tests para código dead

~40+ tests en `tests/unit/PHASE_1/infrastructure/` testean container, boot, lifecycle, diagnostics — todo dead code.

### Problema 4: No hay E2E tests

No existen tests end-to-end que ejecuten el flujo completo:
```
Registrar dispositivo → Generar recomendación → Publicar evento → Consumir en worker
```

### Problema 5: Tests de frontend incompletos

8 tests para ~150 componentes + ~12 módulos. Coverage estimado <20%.

---

## 8. GAPS PRIORITARIOS

| Test que falta | Prioridad | Razón |
|---|---|---|
| Contract tests para repositories | 🔴 CRÍTICA | Los dos sistemas de puertos coexisten sin validación |
| E2E: Device → Recommendation → Event | 🔴 CRÍTICA | Valida flujo completo de negocio |
| Test de auth flow completo | 🔴 CRÍTICA | HIPAA compliance depende de esto |
| Test de multi-tenant isolation | 🔴 CRÍTICA | Security depende de esto |
| Test de RabbitMQ outbox | 🟡 ALTA | Event-driven architecture sin tests |
| Tests de incident router/service | 🟡 ALTA | Dominio principal sin tests dedicados |
| Tests de Celery workers | 🟡 ALTA | Background tasks no probados |
| E2E tests con Playwright | 🟡 ALTA | Frontend coverage bajo |
| Tests de PHASE_5 gateways | 🟡 ALTA | PHASE_5 necesita validación antes de integración |
| Tests de PHASE_2 embedding + rag | 🟡 ALTA | AI kernel necesita tests rigurosos |
| Tests de observability (tracing, logging) | 🟡 MEDIA | OpenTelemetry sin validación |
| Tests de Kubernetes deployment | 🟡 MEDIA | K8s manifests no probados |

---

*Reporte generado: 2026-08-03*
