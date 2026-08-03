# TRAZABILIDAD DE DECISIONES ARQUITECTÓNICAS

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** Auditoría `docs/audit/` completa

---

## CÓMO LEER ESTE DOCUMENTO

```
HALLAZGO DE AUDITORÍA
↓
PROBLEMA
↓
REGLA ARQUITECTÓNICA
↓
DECISIÓN
↓
DOCUMENTOS AFECTADOS
↓
FUTURO CAMBIO DE CÓDIGO
```

Cada fila conecta un hallazgo de la auditoría con la decisión arquitectónica que lo resuelve, el documento que la registra, y el cambio de código futuro.

---

## 1. CÓDIGO MUERTO

### 1.1 DI Container en core/

```
HALLAZGO:
  core/PHASE_1/infrastructure/container/ (19 archivos)
  Nunca importado por apps/ ni por otros PHASEs
  Evidencia: grep -rn "from core.PHASE_1.infrastructure.container" . → vacío

PROBLEMA:
  Dependency Rule violada. Infraestructura en core/.

REGLA: DEPENDENCY_RULES.md Regla 9
  "La infraestructura nunca pertenece a core/."

DECISIÓN:
  Eliminar. Es código muerto.

DOCUMENTOS AFECTADOS:
  - docs/audit/DEAD_CODE_REPORT.md
  - docs/audit/CORRECTION_LIST.md → C2

FUTURO CAMBIO DE CÓDIGO:
  git rm core/PHASE_1/infrastructure/container/
  git commit -m "chore: remove dead DI container"
```

### 1.2 PHASE_2 Runtime

```
HALLAZGO:
  core/PHASE_2/runtime/ (~15 archivos)
  Nunca importado fuera de sí mismo
  Evidencia: grep -rn "from core.PHASE_2.runtime" . → vacío

PROBLEMA:
  Runtime que nunca se ejecuta. Código que nunca se testeó en producción.

REGLA: MIGRATION_PRINCIPLES.md Principio 1
  "Validar antes de migrar."

DECISIÓN:
  Eliminar. Es dead code confirmado.

DOCUMENTOS AFECTADOS:
  - docs/audit/DEAD_CODE_REPORT.md
  - docs/audit/CORRECTION_LIST.md → C4

FUTURO CAMBIO DE CÓDIGO:
  git rm core/PHASE_2/runtime/
  git commit -m "chore: remove dead PHASE_2 runtime"
```

### 1.3 LEGACY

```
HALLAZGO:
  core/LEGACY/ (~20 archivos)
  0 imports externos
  Evidencia: grep -rn "from core.LEGACY" . → vacío fuera de LEGACY/

PROBLEMA:
  Código legacy sin uso, aislamiento total confirmado.

REGLA: MIGRATION_PRINCIPLES.md Principio 1
  "Validar antes de migrar."

DECISIÓN:
  Eliminar.

DOCUMENTOS AFECTADOS:
  - docs/audit/DEAD_CODE_REPORT.md
  - docs/audit/CORRECTION_LIST.md → C5

FUTURO CAMBIO DE CÓDIGO:
  git rm core/LEGACY/
  git commit -m "chore: remove dead LEGACY code"
```

---

## 2. SISTEMAS DE PUERTOS

### 2.1 Dual port system incompatible

```
HALLAZGO:
  core/PHASE_1/domain/*/repositories/ → ABC + Result[Device, str]
  apps/api/app/domain/*/repository.py → Protocol + DeviceModel | None
  Firmas incompatibles. Dos sistemas coexisten.

PROBLEMA:
  Riesgo de inconsistencia. Los servicios usan el sistema de apps/api/,
  no el de core/. Cambios en uno no se reflejan en el otro.

REGLA: ARCHITECTURAL_RULES.md Regla 7
  "Un contrato por Bounded Context."

DECISIÓN:
  Unificar en ABC de core/ como contrato canónico.
  ABC de core/ usa Result[T, E], value objects, y domain objects.
  apps/api implementa el ABC.

  Opción A (seleccionada): Migrar apps/api a usar ABC de core/
  Costo: 1-2 semanas, 20 archivos
  Beneficio: Un sistema de tipos, contract tests posibles

DOCUMENTOS AFECTADOS:
  - docs/audit/PHASE_REPORT.md
  - docs/audit/TECH_DEBT_REPORT.md
  - docs/audit/CORRECTION_LIST.md → A2

FUTURO CAMBIO DE CÓDIGO:
  1. Modificar SQLAlchemyDeviceRepository para retornar Result[Device, str]
  2. Modificar DeviceService para desempacar Result
  3. Actualizar routers para manejar Result
  4. Escribir contract tests
  5. git commit -m "refactor: unify device port system"
```

---

## 3. COMPOSITION ROOT

### 3.1 No existe Composition Root

```
HALLAZGO:
  apps/api/app/main.py no configura DI.
  Dependencias construidas inline en cada Depends() de cada router.
  22 routers × N dependencias inline.
  Evidencia: grep -n "inject\|container\|composition" main.py → vacío

PROBLEMA:
  No hay centralización de la construcción de dependencias.
  Testing requiere mock en cada endpoint.
  Agregar nueva dependencia = modificar N routers.

REGLA: ARCHITECTURAL_RULES.md Regla 2
  "Los Use Cases viven en core/, no en apps/."
  "Toda entrada al sistema utiliza los mismos Use Cases."

DECISIÓN:
  Crear Composition Root con factory functions en apps/api/main.py.
  NO usar DI framework. Factory functions simples.
  NO dependency-injector, NO punq, NO injector.

  Razón: 2 desarrolladores. FastAPI Depends() es suficiente.
  Costo: 3-5 días.
  Beneficio: Un lugar donde se ve qué depende de qué.

DOCUMENTOS AFECTADOS:
  - docs/audit/CI_REPORT.md (CI no corre tests)
  - docs/audit/CORRECTION_LIST.md → C1

FUTURO CAMBIO DE CÓDIGO:
  1. Crear factory functions en main.py
  2. create_device_service(session) → DeviceService
  3. create_incident_service(session) → IncidentService
  4. create_knowledge_service(session) → KnowledgeService
  5. create_recommendation_service(session) → RecommendationService
  6. Actualizar routers uno por uno
  7. git commit -m "feat: implement Composition Root"
```

---

## 4. ACOPLAMIENTOS

### 4.1 PHASE_4 → PHASE_2.infrastructure

```
HALLAZGO:
  core/PHASE_4/foundation/__init__.py:793
  from core.PHASE_2.embeddings.manager import EmbeddingManager
  EmbeddingManager es IMPLEMENTACIÓN, no puerto.

PROBLEMA:
  PHASE_4 conoce detalles de implementación de PHASE_2.
  Si EmbeddingManager cambia, PHASE_4 puede romper.
  Viola DEPENDENCY_RULES.md Regla 3.

REGLA: DEPENDENCY_RULES.md Regla 3
  "Los ports son la frontera pública. Imports de otro Context
   pasan por contracts/."

DECISIÓN:
  Crear Phase2EmbeddingPort (ABC) en PHASE_4/contracts/.
  PHASE_4/adapters/phase2_embedding_adapter.py implementa el puerto.
  PHASE_2 proporciona una implementación local.

  Opción A (seleccionada): ACL en PHASE_4.
  Opción B: Definir puerto en PHASE_2 y PHASE_4 lo consume.

DOCUMENTOS AFECTADOS:
  - docs/audit/PHASE_REPORT.md (PHASE_4)
  - docs/audit/CORRECTION_LIST.md → A3

FUTURO CAMBIO DE CÓDIGO:
  1. Crear core/PHASE_4/contracts/phase2_port.py
  2. Crear core/PHASE_4/adapters/phase2_local_adapter.py
  3. Reemplazar import de EmbeddingManager por Phase2Port
  4. Contract test para Phase2Port
  5. git commit -m "feat: add ACL between PHASE_4 and PHASE_2"
```

---

## 5. INFRAESTRUCTURA EN CORE/

### 5.1 container, boot, lifecycle, diagnostics en core/

```
HALLAZGO:
  core/PHASE_1/infrastructure/ contiene container/, boot/, lifecycle/, diagnostics/
  Son infraestructura de aplicación, no dominio.
  Violan Dependency Rule.

PROBLEMA:
  Clean Architecture dice que la infraestructura pertenece a la capa más externa.
  Pero estos componentes nunca se usan (son dead code).

REGLA: ARCHITECTURAL_RULES.md Regla 9
  "La infraestructura nunca pertenece a core/."

DECISIÓN:
  Como todos son dead code (nunca usados), se eliminan directamente.
  No hay necesidad de moverlos: si no se usan, no importa dónde estén.

  Si en el futuro se necesitan, se implementan en apps/api/.

DOCUMENTOS AFECTADOS:
  - docs/audit/DEAD_CODE_REPORT.md
  - docs/audit/CORRECTION_LIST.md → C2, C3

FUTURO CAMBIO DE CÓDIGO:
  git rm core/PHASE_1/infrastructure/{container,boot,lifecycle,diagnostics}/
  git commit -m "chore: remove unused infrastructure from core"
```

---

## 6. PHASE_5

### 6.1 PHASE_5 no integrado

```
HALLAZGO:
  core/PHASE_5/foundation/gateways/ tiene 5 imports comentados.
  Todos dicen "En producción" — nunca se intentó.
  PHASE_5 funciona con datos hardcodeados.

PROBLEMA:
  PHASE_5 (Multi-Agent) es la funcionalidad más avanzada del producto.
  No está disponible para uso.

REGLA: ARCHITECTURAL_RULES.md Regla 8
  "La comunicación entre Bounded Contexts ocurre por
   eventos o gateways."

DECISIÓN:
  Diseñar e implementar Gateway Pattern.
  PHASE_5 consume PHASE_1, 2, 3, 4 por gateways.

  Gateways definidos en PHASE_5/contracts/:
  - Phase1Gateway (Device context)
  - Phase2Gateway (Embeddings, RAG)
  - Phase3Gateway (Reasoning, Evidence)
  - Phase4Gateway (Clinical RAG)

  Implementaciones locales en PHASE_5/adapters/:
  - phase1_local.py → llama DeviceRepository de core/
  - phase2_local.py → llama EmbeddingManager de PHASE_2
  - phase3_local.py → llama ReasoningPipeline de PHASE_3
  - phase4_local.py → llama ClinicalRAGPipeline de PHASE_4

  En el futuro (microservicios), se reemplazan por:
  - phase1_remote.py → HTTP call a PHASE_1 API
  - phase2_remote.py → HTTP call a PHASE_2 API

DOCUMENTOS AFECTADOS:
  - docs/audit/PHASE_REPORT.md (PHASE_5)
  - docs/audit/CORRECTION_LIST.md → M1

FUTURO CAMBIO DE CÓDIGO:
  1. Crear PHASE_5/contracts/{phase1,phase2,phase3,phase4}_gateway.py
  2. Crear PHASE_5/adapters/{phase1,phase2,phase3,phase4}_local_adapter.py
  3. Descomentar imports en PHASE_5/foundation/gateways/
  4. Escribir contract tests
  5. git commit -m "feat: integrate PHASE_5 with Gateway Pattern"
```

---

## 7. FRONTEND

### 7.1 Acceso directo a Supabase

```
HALLAZGO:
  20 accesses directos a Supabase en 9 archivos de apps/web/src/lib/
  El frontend conoce el schema de la base de datos.
  Si el schema cambia, el frontend rompe directamente.

PROBLEMA:
  Acoplamiento entre frontend y base de datos.
  No hay API layer entre ellos.

REGLA: ARCHITECTURAL_RULES.md Regla 3
  "La infraestructura nunca conoce HTTP."

DECISIÓN:
  Crear packages/sdk/ como SDK tipado.
  Frontend usa SDK → API → Base de datos.
  Feature toggle durante migración para coexistencia.

  Fase 1: Migrar lib/queries.ts → SDK calls
  Fase 2: Migrar lib/storage.ts → API signed URLs
  Fase 3: Migrar AuthProvider.tsx → SDK auth

DOCUMENTOS AFECTADOS:
  - docs/audit/TECH_DEBT_REPORT.md
  - docs/audit/CORRECTION_LIST.md → M3

FUTURO CAMBIO DE CÓDIGO:
  1. Crear packages/sdk/src/client.ts
  2. Crear packages/sdk/src/services/device.service.ts
  3. packages/sdk/src/index.ts
  4. Migrar apps/web/src/lib/queries.ts → SDK calls
  5. Feature flag: USE_SDK=true/false
  6. git commit -m "feat: add SDK package and migrate queries"
```

---

## 8. PHASE_NAMES

### 8.1 PHASE_1, PHASE_2, PHASE_3 son confusos

```
HALLAZGO:
  PHASE_1 = Device Management
  PHASE_2 = AI Kernel
  PHASE_3 = Clinical Intelligence
  PHASE_4 = Knowledge Infrastructure
  PHASE_5 = Multi-Agent

  Nadie recuerda qué es cada PHASE sin consultar documentación.

PROBLEMA:
  Carga cognitiva innecesaria.
  "Necesito el módulo de dispositivos" → "¿Cuál PHASE era?"
  Los números implican orden secuencial que no existe.

REGLA: ARCHITECTURAL_RULES.md Regla 4
  "La IA es un dominio técnico."

DECISIÓN:
  Renombrar PHASE → dominio.

  PHASE_1 → device/
  PHASE_2 → ai/
  PHASE_3 → clinical/
  PHASE_4 → knowledge_infrastructure/ (o ai/knowledge/)
  PHASE_5 → ai/multi_agent/ (o multi_agent/)
  PHASE_7/audit → audit/
  PHASE_7/tenant → tenant/
  PHASE_7/compliance → enterprise/

  PHASE_6 → eliminar (vacío)
  LEGACY → eliminar (dead code)

  Script de migración de imports → git mv → actualización de docs.

  NOTA: Esta decisión tiene costo alto (4-6 semanas, 100+ archivos).
  Solo ejecutar si el equipo está de acuerdo.

DOCUMENTOS AFECTADOS:
  - docs/audit/PHASE_REPORT.md
  - docs/audit/TECH_DEBT_REPORT.md
  - docs/guides/TECH_BIBLE.md
  - docs/guides/CORE_SPECIFICATION.md
  - docs/guides/PROJECT_BOOTSTRAP.md
  - 177 ADRs
  - 427 epics

FUTURO CAMBIO DE CÓDIGO:
  1. Script de migración de imports (find + sed)
  2. git mv core/PHASE_1 core/device
  3. git mv core/PHASE_2 core/ai
  4. git mv core/PHASE_3 core/clinical
  5. Actualizar imports en todos los archivos
  6. git mv core/PHASE_6 (eliminar si existe)
  7. git mv core/LEGACY (eliminar)
  8. Actualizar ADR index
  9. git commit -m "refactor: rename PHASE_X to domain names"
```

---

## 9. CI/CD

### 9.1 CI no corre tests

```
HALLAZGO:
  .github/workflows/ci.yml no tiene job de tests.
  Los tests pueden estar fallando y nadie se entera.
  Ruff usa "|| true" — ignora errores silenciosamente.

PROBLEMA:
  Regresiones no se detectan hasta producción.
  La calidad del código no se mide.

REGLA: MIGRATION_PRINCIPLES.md Principio 1
  "Validar antes de migrar."

DECISIÓN:
  1. Agregar job test-api a ci.yml
  2. Eliminar "|| true" de ruff
  3. Agregar coverage gate

DOCUMENTOS AFECTADOS:
  - docs/audit/CI_REPORT.md
  - docs/audit/CORRECTION_LIST.md → C1, A4

FUTURO CAMBIO DE CÓDIGO:
  1. Modificar .github/workflows/ci.yml
     - Agregar job: test-api
     - pytest con coverage
     - coverage gate: --cov-fail-under=60
  2. Eliminar "|| true" de ruff
  3. git commit -m "ci: add test job and fix ruff"
```

---

## RESUMEN: MAPA DE TRAZABILIDAD

```
Auditoría → Problema → Regla → Decisión → Documento → Cambio
```

| Auditoría | Problema | Regla | Decisión | Doc | Cambio |
|---|---|---|---|---|---|
| CÓDIGO MUERTO | | | | | |
| DI Container dead | Dependency Rule violada | DEP_RULES 9 | Eliminar | DEAD_CODE | git rm |
| PHASE_2 Runtime dead | Nunca usado | MIGRATE 1 | Eliminar | DEAD_CODE | git rm |
| LEGACY dead | Aislamiento total | MIGRATE 1 | Eliminar | DEAD_CODE | git rm |
| PUERTOS | | | | | |
| Dual port system | Incompatibilidad | ARCH_RULES 7 | Unificar en ABC | PHASE_REPORT | Refactor repos |
| COMPOSITION | | | | | |
| No existe | Inline DI | ARCH_RULES 2 | Factory functions | CI_REPORT | main.py |
| ACOPLAMIENTOS | | | | | |
| PHASE_4→PHASE_2 | Import infra | DEP_RULES 3 | ACL con gateway | PHASE_REPORT | contracts/ |
| INFRAESTRUCTURA | | | | | |
| container en core/ | Dependency Rule | ARCH_RULES 9 | Eliminar (dead) | DEAD_CODE | git rm |
| PHASE_5 | | | | | |
| No integrado | 5 imports comentados | ARCH_RULES 8 | Gateway Pattern | PHASE_REPORT | contracts/ |
| FRONTEND | | | | | |
| Supabase directo | Acoplamiento DB | ARCH_RULES 3 | SDK + feature flag | TECH_DEBT | packages/sdk |
| NAMING | | | | | |
| PHASE_X confuso | Carga cognitiva | ARCH_RULES 6 | Renombrar → dominio | PHASE_REPORT | git mv + scripts |
| CI/CD | | | | | |
| Tests no corren | Regresiones ocultas | MIGRATE 1 | Job de tests | CI_REPORT | ci.yml |

---

*Cada decisión arquitectónica debe poder trazarse desde un hallazgo de auditoría hasta un cambio de código.*
