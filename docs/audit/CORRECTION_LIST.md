# CORRECTION LIST — Lista Única de TODO lo que debe corregirse

**Fecha:** 2026-08-03
**Regla:** NO corregir nada. Solo listar.

---

## CRÍTICAS (Resolver en las próximas 2 semanas)

### C1: CI no corre tests
**Ubicación:** `.github/workflows/ci.yml`
**Problema:** El workflow no tiene job de tests. Los tests pueden estar fallando y nadie se entera.
**Evidencia:** `grep -n "pytest\|test" .github/workflows/ci.yml` → vacío
**Acción:** Agregar job `test-api` con pytest + coverage
**Riesgo:** Muy bajo
**Tiempo:** 1 día
**Puede eliminarse:** No
**Dependencias:** Ninguna

### C2: DI Container en core/ — viola Dependency Rule
**Ubicación:** `core/PHASE_1/infrastructure/container/` (19 archivos)
**Problema:** Infraestructura de aplicación vive en core/, violando Clean Architecture
**Evidencia:** `grep -rn "from core.PHASE_1.infrastructure.container" . --include="*.py" | grep -v "container/"` → vacío
**Acción:** Eliminar (es dead code)
**Riesgo:** Muy bajo
**Tiempo:** 30 minutos
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

### C3: Boot + Lifecycle + Diagnostics en core/ — dead code
**Ubicación:** `core/PHASE_1/infrastructure/{boot,lifecycle,diagnostics}/`
**Problema:** Usados solo por PHASE_2/runtime que es dead code
**Evidencia:** `grep -rn "CognitiveBootManager\|CognitiveLifecycleManager" apps/` → vacío
**Acción:** Eliminar (~35 archivos)
**Riesgo:** Muy bajo
**Tiempo:** 1 hora
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

### C4: PHASE_2 Runtime — dead code
**Ubicación:** `core/PHASE_2/runtime/`
**Problema:** Nunca importado fuera de sí mismo
**Evidencia:** `grep -rn "from core.PHASE_2.runtime" . --include="*.py" | grep -v "runtime/"` → vacío
**Acción:** Eliminar (~15 archivos)
**Riesgo:** Muy bajo
**Tiempo:** 30 minutos
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

### C5: LEGACY — aislamiento total
**Ubicación:** `core/LEGACY/`
**Problema:** Código legacy sin uso, 0 imports externos
**Evidencia:** `grep -rn "from core.LEGACY" . --include="*.py" | grep -v "LEGACY/"` → vacío
**Acción:** Eliminar (~20 archivos)
**Riesgo:** Muy bajo
**Tiempo:** 30 minutos
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

### C6: UnitOfWork nunca usado
**Ubicación:** `apps/api/app/infrastructure/unit_of_work.py`
**Problema:** 123 líneas de código que ningún router consume
**Evidencia:** `grep -rn "UnitOfWork" apps/api/app/routers` → vacío
**Acción:** Eliminar
**Riesgo:** Muy bajo
**Tiempo:** 10 minutos
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

### C7: CircuitBreaker nunca usado
**Ubicación:** `apps/api/app/providers/circuit_breaker.py`
**Problema:** Definido pero nunca instanciado en routers ni servicios
**Evidencia:** `grep -rn "CircuitBreaker" apps/api/app/routers apps/api/app/services` → vacío
**Acción:** Eliminar
**Riesgo:** Muy bajo
**Tiempo:** 10 minutos
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

### C8: 4× RepositoryImpl nunca instanciados
**Ubicación:** `apps/api/app/infrastructure/repositories/{device,incident,knowledge,recommendation}.py`
**Problema:** Las clases `*RepositoryImpl` nunca se importan — routers usan `SQLAlchemy*Repository`
**Evidencia:** `grep -rn "DeviceRepositoryImpl\|IncidentRepositoryImpl" apps/api/app --include="*.py" | grep -v "repositories/"` → vacío
**Acción:** Eliminar las clases `*RepositoryImpl` de cada archivo
**Riesgo:** Muy bajo
**Tiempo:** 30 minutos
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

### C9: Events duplicados en apps/api/app/
**Ubicación:** `apps/api/app/events/{publisher,outbox}.py`
**Problema:** Duplican `infrastructure/events.py` y `infrastructure/messaging/outbox.py`
**Evidencia:** `grep -rn "from app.events" apps/api/app --include="*.py" | grep -v "events.py\|messaging"` → vacío
**Acción:** Eliminar la carpeta `apps/api/app/events/`
**Riesgo:** Muy bajo
**Tiempo:** 10 minutos
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

### C10: Integrations stubs nunca usados
**Ubicación:** `apps/api/app/integrations/{mqtt_client,dicom_client,hl7_listener,fhir_client}.py`
**Problema:** Stubs sin uso
**Evidencia:** `grep -rn "from app.integrations" apps/api/app --include="*.py"` → vacío
**Acción:** Eliminar o marcar como EXPERIMENTAL
**Riesgo:** Muy bajo
**Tiempo:** 10 minutos
**Puede eliminarse:** Sí, inmediatamente
**Dependencias:** Ninguna

---

## ALTAS (Resolver en 2-4 semanas)

### A1: Composition Root no existe
**Ubicación:** `apps/api/app/main.py`
**Problema:** Dependencias construidas inline en cada router — sin centralización
**Evidencia:** `grep -n "inject\|container\|composition" apps/api/app/main.py` → vacío
**Acción:** Crear factory functions en main.py: `create_device_service(session)`
**Riesgo:** Medio — puede romper tests existentes
**Tiempo:** 3-5 días
**Puede eliminarse:** No
**Dependencias:** Ninguna
**Mitigación:** Tests de regresión + rollback con git

### A2: Sistema dual de puertos incompatible
**Ubicación:** `core/PHASE_1/domain/*/repositories/` vs `apps/api/app/domain/*/repository.py`
**Problema:** Dos interfaces incompatibles. Servicios usan la de apps/api/, no la de core/.
**Evidencia:** ABC usa `Result[Device, str]`, Protocol usa `DeviceModel | None`
**Acción:** Decidir cuál es el contrato canónico (recomendación: ABC de core/)
**Riesgo:** Alto — requiere cambiar 4 repositories + servicios
**Tiempo:** 1-2 semanas
**Dependencias:** A1 (Composition Root primero)

### A3: PHASE_4 importa infraestructura de PHASE_2
**Ubicación:** `core/PHASE_4/foundation/__init__.py:793`
**Problema:** Importa `EmbeddingManager` (implementación) en lugar de puerto
**Evidencia:** `from core.PHASE_2.embeddings.manager import EmbeddingManager`
**Acción:** Crear `Phase2EmbeddingPort` (ABC) en PHASE_4/contracts/ y adapter que implemente
**Riesgo:** Medio
**Tiempo:** 1-2 semanas
**Dependencias:** A2

### A4: Ruff ignora errores con "|| true"
**Ubicación:** `.github/workflows/ci.yml`
**Problema:** `ruff check apps/api/ --ignore E501 || true` — errores ignorados
**Evidencia:** El `|| true` al final del comando
**Acción:** Eliminar `|| true` y dejar que ruff falle el job si hay errores
**Riesgo:** Muy bajo
**Tiempo:** 10 minutos
**Dependencias:** Ninguna

### A5: Tests para código dead en infrastructure/
**Ubicación:** `tests/unit/PHASE_1/infrastructure/{boot,container,diagnostics,lifecycle}/`
**Problema:** ~40 tests testean código dead
**Evidencia:** Los archivos que testean son dead (C2, C3)
**Acción:** Eliminar tests junto con el código que testean
**Riesgo:** Muy bajo
**Tiempo:** 30 minutos
**Dependencias:** C2, C3

---

## MEDIAS (Resolver en 1-3 meses)

### M1: PHASE_5 no integrado — Gateway Pattern
**Ubicación:** `core/PHASE_5/foundation/gateways/`
**Problema:** 5 imports comentados, PHASE_5 funciona con placeholders
**Acción:** Diseñar e implementar 4 gateways: Phase1Gateway, Phase2Gateway, Phase3Gateway, Phase4Gateway
**Tiempo:** 2-3 semanas
**Riesgo:** Medio

### M2: Contract tests no existen
**Ubicación:** `tests/contract/` (no existe)
**Problema:** No hay validación de que adapters cumplen puertos
**Acción:** Crear tests/contract/ con tests para DeviceRepository, IncidentRepository, etc.
**Tiempo:** 1 semana
**Riesgo:** Bajo
**Dependencias:** A2

### M3: Frontend con 20 accesses directos a Supabase
**Ubicación:** `apps/web/src/lib/{queries,supabase,storage}.ts`
**Problema:** Acoplamiento directo con la base de datos
**Acción:** Crear packages/sdk/ y migrar gradualmente con feature toggle
**Tiempo:** 2-4 semanas
**Riesgo:** Medio-alto

### M4: PHASE_2 macro-módulo con duplicación
**Ubicación:** `core/PHASE_2/{ai,cognitive}/`
**Problema:** `ai/rag` vs `cognitive/rag`, `ai/memory` vs `cognitive/memory`, etc.
**Acción:** Investigar si son duplicados reales → consolidar o separar
**Tiempo:** 2 semanas de investigación
**Riesgo:** Bajo

### M5: PHASE_7 infrastructure/ y observability/ en core/
**Ubicación:** `core/PHASE_7/{infrastructure,observability}/`
**Problema:** Plataforma vive en core/, debería vivir en `platform/` o `infra/`
**Acción:** Decidir si mover a `platform/` o mantener en PHASE_7 como decisión deliberada
**Tiempo:** 1 semana
**Riesgo:** Medio

### M6: packages/ stubs vacíos
**Ubicación:** `packages/{sdk,schemas,prompts,shared}/`
**Problema:** 4 packages npm vacíos
**Acción:** Llenarlos con implementación real o eliminarlos
**Tiempo:** 4 semanas (si se llenan) / 1 hora (si se eliminan)
**Riesgo:** Bajo

### M7: Docker-compose no tiene RabbitMQ
**Ubicación:** `docker-compose.yml`
**Problema:** aio-pika en pyproject.toml pero ningún servicio de RabbitMQ
**Acción:** Agregar servicio RabbitMQ a docker-compose.yml
**Tiempo:** 1 hora
**Riesgo:** Bajo

---

## BAJAS (Resolver cuando haya tiempo)

### B1: PHASE_1/diagnostic/ carpeta vacía → eliminar
**Tiempo:** 5 minutos

### B2: PHASE_2/ai/di/ carpeta vacía → eliminar
**Tiempo:** 5 minutos

### B3: Enterprise stubs en apps/api/app/enterprise/ → eliminar
**Tiempo:** 10 minutos

### B4: Vault client stub → eliminar o implementar
**Tiempo:** 10 minutos

### B5: Diagnosis + patient models sin uso → investigar
**Tiempo:** 2 horas

### B6: apps/api/app/models/ duplicado de infrastructure/models/
**Tiempo:** 2 horas de investigación

### B7: MyPy en modo no-strict
**Tiempo:** 1 semana para habilitar strict progresivamente

### B8: Lint de core/ no existe en CI
**Tiempo:** 1 día

### B9: Frontend CI no existe
**Tiempo:** 1 día

---

## RESUMEN

| Prioridad | Items | Tiempo total |
|---|---|---|
| CRÍTICAS | 10 | ~4 horas |
| ALTAS | 5 | ~3 semanas |
| MEDIAS | 7 | ~2-3 meses |
| BAJAS | 9 | ~2 semanas |
| **TOTAL** | **31 items** | **~4 meses** |

**Para un equipo de 2 desarrolladores.**

---

*Lista generada: 2026-08-03*
