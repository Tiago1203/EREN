# Plan de Migración — EREN

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** `docs/architecture-validation.md` + `docs/architecture-tobe.md`
**Restricción:** NO modificar código durante esta fase. Este documento es solo un roadmap.

---

## ESTRATEGIA GENERAL

### Principio: Transformación incremental sin停下

> "No rewrite. Only evolution."

Ningún paso requiere tirar y reescribir. Cada fase es:
- **Auto-contenida** — no depende de fases futuras
- **Reversible** — se puede hacer rollback con `git revert`
- **Probable** — tests en cada paso

### Orden de trabajo

```
1. Limpiar código muerto        ← Sin riesgo, alto valor
2. Crear Composition Root        ← Riesgo bajo, valor alto
3. Migrar puertos duplicados     ← Riesgo medio, valor alto
4. Mover infraestructura          ← Riesgo alto, valor arquitectónico
5. Eliminar PHASE_5 isolates     ← Riesgo medio, requiere decisión
6. Migrar frontend               ← Riesgo alto, requiere coordinación
```

---

## FASE 0 — Auditoría y baseline

**Objetivo:** Establecer línea base antes de cualquier cambio.

### 0.1 Capturar estado actual

```bash
# Generar snapshot de dependencias
pip install pipreqs
pipreqs apps/api --force
pipreqs core/PHASE_1 --force

# Ejecutar tests actuales
cd apps/api && pytest --tb=short -q 2>&1 | tee /tmp/baseline_tests.txt

# Verificar cobertura actual
pytest --cov=app --cov=core --cov-report=term-missing 2>&1 | tee /tmp/coverage.txt
```

**Archivos afectados:** Ninguno
**Riesgo:** Ninguno
**Impacto:** Documentación
**Rollback:** Ninguno necesario
**Tiempo estimado:** 2 horas

### 0.2 Definir contract tests base

Crear tests de contrato para los puertos existentes.

```python
# tests/contract/test_device_repository_contract.py
# tests/contract/test_incident_repository_contract.py
# tests/contract/test_knowledge_repository_contract.py
```

**Archivos afectados:** `tests/contract/`
**Riesgo:** Bajo (solo se crean archivos nuevos)
**Impacto:** Tests de regresión para migraciones futuras
**Rollback:** `git checkout HEAD -- tests/contract/`
**Tiempo estimado:** 4 horas

---

## FASE 1 — Limpieza de código muerto

**Objetivo:** Eliminar complejidad sin valor.

**Riesgo:** ❌ Muy bajo — solo eliminación de archivos no usados
**Impacto:** Alto — reduce deuda técnica, mejora mantenibilidad
**Tiempo estimado:** 1-2 días

### 1.1 Eliminar DI Container no usado

```
Archivos a eliminar:
  core/PHASE_1/infrastructure/container/ (19 archivos)
```

**Verificación:**
```bash
# Confirmar que no hay imports
grep -rn "from core.PHASE_1.infrastructure.container" . --include="*.py"
# Esperado: solo dentro de container/ mismo

# Confirmar que container no está referenciado
grep -rn "CognitiveContainer\|get_container" . --include="*.py" | grep -v "container/"
```

**Archivos afectados:** `core/PHASE_1/infrastructure/container/`
**Riesgo:** ❌ Muy bajo — confirmado dead code
**Impacto:** Reduce 19 archivos de complejidad
**Rollback:** `git checkout HEAD -- core/PHASE_1/infrastructure/container/`
**Tiempo estimado:** 30 minutos

### 1.2 Eliminar PHASE_2 Runtime no usado

```
Archivos a eliminar:
  core/PHASE_2/runtime/ (todo el directorio)
```

**Verificación:**
```bash
grep -rn "CognitiveRuntime\|from core.PHASE_2.runtime" . --include="*.py"
# Esperado: vacío fuera de core/PHASE_2/runtime/
```

**Archivos afectados:** `core/PHASE_2/runtime/`
**Riesgo:** ❌ Muy bajo — confirmado dead code
**Impacto:** Reduce ~500 líneas no usadas
**Rollback:** `git checkout HEAD -- core/PHASE_2/runtime/`
**Tiempo estimado:** 30 minutos

### 1.3 Eliminar LEGACY

```
Archivos a eliminar:
  core/LEGACY/ (todo el directorio)
```

**Verificación:**
```bash
grep -rn "from core.LEGACY" . --include="*.py"
# Esperado: vacío
```

**Archivos afectados:** `core/LEGACY/`
**Riesgo:** ❌ Muy bajo — confirmado dead code
**Impacto:** Reduce 20+ archivos
**Rollback:** `git checkout HEAD -- core/LEGACY/`
**Tiempo estimado:** 30 minutos

### 1.4 Eliminar RepositoryImpl dead en apps/api

```
Archivos a eliminar:
  apps/api/app/infrastructure/repositories/device.py  (clase DeviceRepositoryImpl)
  apps/api/app/infrastructure/repositories/incident.py (clase IncidentRepositoryImpl)
  apps/api/app/infrastructure/repositories/knowledge.py (clase KnowledgeRepositoryImpl)
  apps/api/app/infrastructure/repositories/recommendation.py (clase RecommendationRepositoryImpl)
```

**Acción:** Mantener solo `apps/api/app/domain/*/repository.py` (el que tiene Protocol + SQLAlchemyDeviceRepository). Eliminar la clase `*RepositoryImpl` de `apps/api/app/infrastructure/repositories/`.

**Verificación:**
```bash
# Verificar que los servicios usan el Protocol correcto
grep -rn "from app.domain" apps/api/app/domain/ --include="*.py"
grep -rn "DeviceRepositoryImpl\|IncidentRepositoryImpl" apps/api/app --include="*.py"
# Esperado: vacío fuera de infraestructura/repositories/
```

**Archivos afectados:** 4 archivos en `apps/api/app/infrastructure/repositories/`
**Riesgo:** ❌ Muy bajo — confirmado que estas clases nunca se instancian
**Impacto:** Reduce confusión (2 interfaces para el mismo concepto)
**Rollback:** `git checkout HEAD -- apps/api/app/infrastructure/repositories/`
**Tiempo estimado:** 2 horas

### 1.5 Eliminar UnitOfWork no usado

```
Archivos a eliminar:
  apps/api/app/infrastructure/unit_of_work.py
```

**Verificación:**
```bash
grep -rn "UnitOfWork\|unit_of_work" apps/api/app/routers apps/api/app/services --include="*.py"
# Esperado: vacío
```

**Archivos afectados:** `apps/api/app/infrastructure/unit_of_work.py`
**Riesgo:** ❌ Muy bajo
**Impacto:** Reduce 123 líneas no usadas
**Rollback:** `git checkout HEAD -- apps/api/app/infrastructure/unit_of_work.py`
**Tiempo estimado:** 30 minutos

### 1.6 Eliminar CircuitBreaker no usado

```
Archivos a eliminar:
  apps/api/app/providers/circuit_breaker.py
```

**Verificación:**
```bash
grep -rn "CircuitBreaker\|circuit_breaker" apps/api/app/routers apps/api/app/services --include="*.py"
# Esperado: vacío
```

**Archivos afectados:** `apps/api/app/providers/circuit_breaker.py`
**Riesgo:** ❌ Muy bajo
**Impacto:** Reduce 150+ líneas no usadas
**Rollback:** `git checkout HEAD -- apps/api/app/providers/circuit_breaker.py`
**Tiempo estimado:** 30 minutos

### 1.7 Eliminar carpetas vacías

```
Archivos a eliminar:
  core/PHASE_1/infrastructure/diagnostic/
  core/PHASE_2/ai/di/
```

**Verificación:**
```bash
find core/PHASE_1/infrastructure/diagnostic -name "*.py" | grep -v __init__ | grep -v __pycache__
find core/PHASE_2/ai/di -name "*.py" | grep -v __init__ | grep -v __pycache__
```

**Archivos afectados:** 2 carpetas
**Riesgo:** ❌ Muy bajo
**Impacto:** Limpieza
**Rollback:** `git checkout HEAD -- core/PHASE_1/infrastructure/diagnostic/ -- core/PHASE_2/ai/di/`
**Tiempo estimado:** 15 minutos

### Resumen FASE 1

| Paso | Archivos | Riesgo | Tiempo |
|---|---|---|---|
| 1.1 | ~19 | Muy bajo | 30 min |
| 1.2 | ~15 | Muy bajo | 30 min |
| 1.3 | ~20 | Muy bajo | 30 min |
| 1.4 | 4 | Muy bajo | 2 hr |
| 1.5 | 1 | Muy bajo | 30 min |
| 1.6 | 1 | Muy bajo | 30 min |
| 1.7 | 2 dirs | Muy bajo | 15 min |
| **Total** | **~60 archivos** | **Muy bajo** | **~5 horas** |

---

## FASE 2 — Composition Root centralizado

**Objetivo:** Crear un container DI real en `apps/api/app/main.py`.

**Riesgo:** ⚠️ Medio — cambios en cómo se construyen las dependencias
**Impacto:** Alto — elimina construcción manual inline en routers
**Tiempo estimado:** 3-5 días
**Requisito previo:** FASE 1 (completa)

### 2.1 Evaluar opciones de DI

| Opción | Pros | Contras | Tiempo |
|---|---|---|---|
| **Manual (Factory functions)** | Sin dependencias nuevas, simple | Boilerplate | 3 días |
| **dependency-injector** | Full-featured, bien documentado | Dependencia nueva | 5 días |
| **punq** | Ligero, simple | Menos features | 3 días |
| **Házel** | Nativo Python | Proyecto nuevo | 7 días |

**Recomendación:** Punq o manual. Para un equipo de 2 desarrolladores, la simplicidad vale más que las features.

### 2.2 Definir el grafo de dependencias

Crear `apps/api/app/infrastructure/container.py`:

```python
# apps/api/app/infrastructure/container.py
"""Dependency Injection Container para apps/api."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class Container:
    """Simple DI Container — Composition Root."""

    def __init__(self) -> None:
        self._factories: dict[type, Callable[[Container], Any]] = {}
        self._singletons: dict[type, Any] = {}
        self._session_factory: Any = None

    def register(
        self,
        type_: type[T],
        factory: Callable[[Container], T],
    ) -> None:
        self._factories[type_] = factory

    def get(self, type_: type[T]) -> T:
        if type_ in self._singletons:
            return self._singletons[type_]

        if type_ not in self._factories:
            raise KeyError(f"Type {type_} not registered in container")

        instance = self._factories[type_](self)
        self._singletons[type_] = instance
        return instance

    def get_scoped(self, type_: type[T], scope: Any) -> T:
        # Para AsyncSession — crear una nueva en cada request
        return self._factories[type_](self)
```

### 2.3 Registrar todas las dependencias

Modificar `apps/api/app/main.py`:

```python
# apps/api/app/main.py — AGREGAR al final del archivo
def create_container() -> Container:
    container = Container()

    # Database
    container.register(AsyncEngine, create_async_engine)
    container.register(SessionFactory, create_session_factory)

    # Repositories
    container.register(DeviceRepository, lambda c: SQLAlchemyDeviceRepository(c.get(AsyncSession)))
    container.register(IncidentRepository, lambda c: SQLAlchemyIncidentRepository(c.get(AsyncSession)))
    container.register(KnowledgeRepository, lambda c: SQLAlchemyKnowledgeRepository(c.get(AsyncSession)))
    container.register(RecommendationRepository, lambda c: SQLAlchemyRecommendationRepository(c.get(AsyncSession)))

    # Event Bus
    container.register(EventBus, lambda c: RabbitMQEventBus(c.get_rabbitmq()))

    # Services
    container.register(DeviceService, lambda c: DeviceService(
        repository=c.get(DeviceRepository),
        event_bus=c.get(EventBus),
    ))
    container.register(IncidentService, lambda c: IncidentService(
        repository=c.get(IncidentRepository),
        event_bus=c.get(EventBus),
    ))

    return container
```

### 2.4 Actualizar routers

Cambiar de:

```python
# ANTES
async def get_device_service(db: Annotated[AsyncSession, Depends(get_db)]) -> DeviceService:
    repository = SQLAlchemyDeviceRepository(db)
    return DeviceService(repository=repository, outbox=outbox)
```

A:

```python
# DESPUÉS
def get_device_service(container: Container) -> DeviceService:
    return container.get(DeviceService)
```

### 2.5 Testing con container

Crear `tests/conftest.py` con container de test:

```python
@pytest.fixture
def test_container() -> Container:
    container = Container()
    container.register(DeviceRepository, lambda _: InMemoryDeviceRepository())
    container.register(EventBus, lambda _: MockEventBus())
    container.register(DeviceService, lambda c: DeviceService(c.get(DeviceRepository)))
    return container
```

**Archivos afectados:**
- `apps/api/app/main.py` — agregar `create_container()`
- `apps/api/app/infrastructure/container.py` — crear container
- `apps/api/app/routers/devices.py` — actualizar `get_device_service()`
- `apps/api/app/routers/work_orders.py` — actualizar
- `apps/api/app/routers/incidents.py` — actualizar
- `apps/api/tests/conftest.py` — agregar test container

**Riesgo:** ⚠️ Medio
- Los tests existentes pueden romper porque ahora las dependencias se injectan diferente
- Mitigación: mantener las funciones `get_db` existentes como fallback

**Impacto:**
- Un lugar para todas las dependencias
- Tests más fáciles con container de test
- Lazy initialization

**Rollback:** `git checkout HEAD -- apps/api/app/main.py apps/api/app/infrastructure/ apps/api/app/routers/`
**Tiempo estimado:** 3-5 días

---

## FASE 3 — Unificar puertos duplicados

**Objetivo:** Eliminar las dos interfaces de repositorio. Elegir una.

**Riesgo:** ⚠️ Medio-alto — requiere cambiar implementación
**Impacto:** Alto — elimina duplicación y confusión
**Tiempo estimado:** 1-2 semanas
**Requisito previo:** FASE 2 (completa)

### 3.1 Decisión: ¿Qué puerto usar?

**Opción A — Mantener Protocol de apps/api (Recomendada para este equipo)**

Razón: El equipo ya usa los Protocol de `apps/api/app/domain/`. Cambiar a los ABC de `core/PHASE_1` requiere reescribir los servicios y adapters. Con 2 desarrolladores, el costo es alto.

**Acción:**
1. Eliminar los ABC de `core/PHASE_1/domain/*/repositories/` que no se usan fuera de `core/`
2. Mantener los Protocol de `apps/api/app/domain/*/repository.py`
3. Asegurar que todos los adapters en `apps/api/infrastructure/repositories/` implementen el Protocol de `apps/api/app/domain/`

**Archivos afectados:**
- `core/PHASE_1/domain/device/domain/repositories/device_repository.py` → eliminar ABC, mantener exports del Protocol
- `core/PHASE_1/domain/incident/domain/repositories/incident_repository.py` → mismo
- `core/PHASE_1/domain/knowledge/domain/repositories/knowledge_repository.py` → mismo
- `core/PHASE_3/recommendation/domain/repositories/recommendation_repository.py` → mismo

**Opción B — Migrar a ABC de core/ (Recomendada para arquitectura a largo plazo)**

Razón: Los ABC de `core/` son más robustos (Result[T], value objects). Si el objetivo es migrar a microservicios eventualmente, esta opción facilita la separación.

**Acción:**
1. Modificar los Protocol en `apps/api/app/domain/` para que coincidan con los ABC de `core/`
2. Cambiar `SQLAlchemyDeviceRepository` para retornar `Result[Device, str]` en lugar de `DeviceModel | None`
3. Actualizar los servicios para manejar `Result`
4. Ejecutar contract tests

### 3.2 Implementar Opción B (si se elige)

**Paso 1:** Definir el contrato común

```python
# Definir en core/PHASE_1/domain/device/domain/repositories/device_repository.py
# como autoridad. apps/api lo importa.
```

**Paso 2:** Hacer que el adapter use el contrato

```python
# apps/api/app/infrastructure/repositories/device.py
from core.PHASE_1.domain.device.domain.repositories import DeviceRepository

class SQLAlchemyDeviceRepository(DeviceRepository):
    """Implementa el puerto de core/PHASE_1."""

    async def save(self, device: Device) -> Result[Device, str]:
        # Conversión Device → DeviceModel → persist → Device
        ...
```

**Paso 3:** Actualizar servicios

```python
# apps/api/app/domain/device/service.py
async def register_device(self, data: DeviceCreate) -> Result[Device, str]:
    result = await self.repository.save(device)
    return result  # Ya es Result[Device, str]
```

**Paso 4:** Ejecutar contract tests

**Archivos afectados:**
- `core/PHASE_1/domain/device/domain/repositories/device_repository.py` — definir contrato
- `apps/api/app/infrastructure/repositories/device.py` — implementar contrato
- `apps/api/app/domain/device/service.py` — usar Result
- `apps/api/app/routers/devices.py` — desempacar Result
- 20+ archivos

**Riesgo:** ⚠️ Alto — cambia el contrato de todos los repositorios
- Mitigación: contract tests antes de empezar
- Mitigación: hacer un PHASE a la vez (Device → Incident → Knowledge → Recommendation)

**Impacto:**
- Un contrato por BC
- Type safety mejorado
- PHASE_4 y PHASE_5 pueden usar los mismos puertos

**Rollback:** `git checkout HEAD -- apps/api/app/infrastructure/repositories/ apps/api/app/domain/ core/PHASE_1/domain/`
**Tiempo estimado:** 1-2 semanas (4 días por BC × 4 BCs = 16 días si se hace todo)

---

## FASE 4 — Mover infraestructura de core/ a apps/api/

**Objetivo:** Resolver la violación de la Dependency Rule.

**Riesgo:** ⚠️⚠️ Alto — mueve archivos entre carpetas, puede romper imports
**Impacto:** Arquitectónico — habilita la extracción de microservicios
**Tiempo estimado:** 2-3 semanas
**Requisito previo:** FASE 3 (completa)

### 4.1 Inventario de infraestructura en core/

| Carpeta | Archivos | Tipo | Mover a |
|---|---|---|---|
| `core/PHASE_1/infrastructure/container/` | 19 | DI Container | ~~Eliminado en FASE 1~~ |
| `core/PHASE_1/infrastructure/boot/` | ~8 | Bootstrap | `apps/api/app/infrastructure/bootstrap/` |
| `core/PHASE_1/infrastructure/lifecycle/` | ~6 | Lifecycle | `apps/api/app/infrastructure/lifecycle/` |
| `core/PHASE_1/infrastructure/diagnostics/` | 19 | Health checks | `apps/api/app/infrastructure/health/` |
| `core/PHASE_1/infrastructure/events/` | ~10 | Event bus | `apps/api/app/infrastructure/messaging/events/` |
| `core/PHASE_1/infrastructure/contracts/` | 21 | Puertos | **MANTENER en core/** (son interfaces) |

### 4.2 Plan de migración (eventos como ejemplo)

**Paso 1:** Copiar archivos

```bash
cp -r core/PHASE_1/infrastructure/events/ apps/api/app/infrastructure/messaging/core_events/
```

**Paso 2:** Actualizar imports en apps/api

```bash
# Encontrar todos los imports a core/PHASE_1/infrastructure/events/
grep -rn "from core.PHASE_1.infrastructure.events" apps/ --include="*.py"
# Actualizar a: from app.infrastructure.messaging.core_events
```

**Paso 3:** Verificar PHASE_2

```bash
# PHASE_2 también importa events de PHASE_1
grep -rn "from core.PHASE_1.infrastructure.events" core/PHASE_2 --include="*.py"
```

**⚠️ PROBLEMA CRÍTICO:** PHASE_2 importa `core/PHASE_1/infrastructure/events/`. Si movemos los eventos fuera de core/, PHASE_2 rompe.

**Solución:** Mantener los eventos en core/ como dominio de events (el concepto), pero mover la implementación de RabbitMQ a apps/api.

```
core/PHASE_1/domain/events/         ← Dominio de eventos (Value Objects, Events)
apps/api/app/infrastructure/events/   ← Implementación: RabbitMQ, Outbox
```

### 4.3 Mapeo corregido

```
SE MUEVE:
  core/PHASE_1/infrastructure/boot/          → apps/api/app/infrastructure/bootstrap/
  core/PHASE_1/infrastructure/lifecycle/     → apps/api/app/infrastructure/lifecycle/
  core/PHASE_1/infrastructure/diagnostics/   → apps/api/app/infrastructure/health/

SE MANTIENE en core/:
  core/PHASE_1/infrastructure/contracts/     → Puertos (interfaces)
  core/PHASE_1/infrastructure/shared/         → Tipos compartidos
  core/PHASE_1/domain/                        → Dominio

⚠️ PROBLEMA:
  PHASE_2/runtime/runtime.py importa:
    - CognitiveContainer       → Eliminado en FASE 1
    - EventBus                → Si se mueve, PHASE_2 rompe
    - CognitiveBootManager     → Si se mueve, PHASE_2 rompe
    - CognitiveLifecycleManager → Si se mueve, PHASE_2 rompe
```

**Conclusión:** No se puede mover la infraestructura de core/ sin resolver primero PHASE_2.

**Opción 1:** Eliminar PHASE_2/runtime/ primero (FASE 1.2), luego mover infraestructura.
**Opción 2:** Mantener la infraestructura de core/ mientras PHASE_2 la use. Documentar como "technical debt — PHASE_2 isolated".

### 4.4 Recomendación de ejecución

```
Si PHASE_2 NO se va a usar:
  1. Ejecutar FASE 1.2 (eliminar PHASE_2/runtime/)
  2. Mover infraestructura de core/ a apps/api/
  3. Limpiar imports en apps/api

Si PHASE_2 SÍ se va a usar:
  1. Postergar esta fase indefinidamente
  2. Documentar como restricción arquitectónica
  3. No Claim "Clean Architecture" hasta que se resuelva PHASE_2
```

**Archivos afectados:** ~50+ archivos movidos
**Riesgo:** ⚠️⚠️⚠️ Muy alto — puede romper 100+ imports
**Mitigación:**
- Script automático para actualizar imports
- Contract tests
- Tests de integración antes y después

**Rollback:** `git checkout HEAD -- core/PHASE_1/infrastructure/ apps/api/app/infrastructure/`
**Tiempo estimado:** 2-3 semanas

---

## FASE 5 — Resolver PHASE_5

**Objetivo:** Decidir el destino de los 5 imports comentados.

**Riesgo:** ⚠️⚠️ Medio-alto
**Impacto:** PHASE_5 se convierte en módulo útil o se elimina
**Tiempo estimado:** 1-3 semanas (depende de la decisión)

### 5.1 Opciones

**Opción A — Integrar PHASE_5 con PHASE_1-4**

1. Descomentar los 5 imports
2. Crear adapters que implementen los contratos de PHASE_1, 2, 3, 4
3. Ejecutar tests de integración
4. Conectar con los servicios existentes

**Opción B — Eliminar PHASE_5**

1. Eliminar `core/PHASE_5/` completo
2. Limpiar referencias en otros archivos
3. Documentar que PHASE_5 fue prototipado pero no integrado

**Opción C — Postergar PHASE_5**

1. No hacer nada ahora
2. Documentar que PHASE_5 es "futuro"
3. No mantener código de integración commented (confunde)

### 5.2 Recomendación

**Opción B** (eliminar) por ahora. PHASE_5 fue diseñado para依赖 PHASE_1-4 pero la integración nunca se completó. Mantener código commented de integración genera confusión. Si en el futuro se necesita PHASE_5, se reimplementa con la arquitectura corregida.

**Archivos afectados:** `core/PHASE_5/` (~100+ archivos)
**Riesgo:** ⚠️ Medio — solo si algo depende de PHASE_5
**Verificación:**
```bash
grep -rn "from core.PHASE_5" core/ apps/ --include="*.py" | grep -v "PHASE_5/"
# Esperado: vacío
```
**Rollback:** `git checkout HEAD -- core/PHASE_5/`
**Tiempo estimado:** 1 día (si se elimina) o 2-3 semanas (si se integra)

---

## FASE 6 — Migración de frontend

**Objetivo:** Eliminar acceso directo a Supabase. Usar API/SDK.

**Riesgo:** ⚠️⚠️⚠️ Alto — cambia la arquitectura de datos del frontend
**Impacto:** Alto — frontend queda acoplado a la API
**Tiempo estimado:** 2-4 semanas
**Requisito previo:** FASE 2 + FASE 3 (Composition Root + puertos unificados)

### 6.1 Inventario de migraciones

| Ubicación | Tipo | Riesgo | Esfuerzo |
|---|---|---|---|
| `lib/queries.ts` | 4 queries → SDK calls | ⚠️ Bajo | 2 horas |
| `lib/storage.ts` | 3 uploads → API signed URLs | ⚠️⚠️ Medio | 4 horas |
| `modules/equipos/` | 2 calls → SDK | ⚠️ Bajo | 2 horas |
| `modules/mantenimientos/` | 1 delete → SDK | ⚠️ Bajo | 1 hora |
| `modules/establecimientos/` | 2 auth calls → SDK | ⚠️⚠️ Medio | 3 horas |
| `components/ui/FileViewer.tsx` | 2 updates → SDK | ⚠️ Bajo | 2 horas |
| `components/auth/AuthProvider.tsx` | 6 auth calls → SDK | ⚠️⚠️⚠️ Alto | 8 horas |
| `app/api/create-user/route.ts` | 1 call → SDK | ⚠️ Bajo | 1 hora |
| `modules/administration/` | 1 query → SDK | ⚠️ Bajo | 1 hora |

### 6.2 Crear SDK cliente

```typescript
// packages/sdk/src/index.ts
export class ErenSDK {
  constructor(private baseUrl: string, private apiKey: string) {}

  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    return res.json();
  }

  async post<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(body),
    });
    return res.json();
  }

  devices = new DevicesClient(this);
  mantenimientos = new MantenimientosClient(this);
  // ...
}
```

### 6.3 Plan de migración por fase

**Fase 6.1 — Queries (bajo riesgo)**

Migrar `lib/queries.ts` → SDK calls.

```typescript
// ANTES
import { supabase } from './supabase'
const { data } = await supabase.from('equipos').select('*')

// DESPUÉS
import { erenSdk } from '@/lib/eren-sdk'
const data = await erenSdk.devices.list({ tenantId })
```

**Fase 6.2 — Equipos y mantenimientos**

Migrar `modules/equipos/` y `modules/mantenimientos/`.

**Fase 6.3 — Storage**

Migrar `lib/storage.ts` para usar signed URLs del API.

```typescript
// ANTES
const { data } = await supabase.storage.from(bucket).upload(path, file)

// DESPUÉS
const { signedUrl } = await erenSdk.storage.getUploadUrl(path)
const { error } = await fetch(signedUrl, { method: 'PUT', body: file })
```

**Fase 6.4 — Auth**

⚠️ La auth es la más compleja. Supabase Auth tiene session management, cookies, etc. Decidir:
- Opción A: Mantener Supabase Auth (es bueno como auth provider), solo migrar DB access
- Opción B: Migrar a API-based auth con JWT

**Recomendación:** Opción A. Supabase Auth es maduro y bien mantenido. No hay razón para reescribirlo.

### 6.4 Estrategia de coexistencia

Durante la migración, permitir acceso dual:

```typescript
// lib/supabase.ts
export const supabase = createBrowserClient(...)

// lib/eren-sdk.ts
export const erenSdk = new ErenSDK(...)

// Flag de feature toggle
const USE_SDK = process.env.NEXT_PUBLIC_USE_EREN_SDK === 'true'
```

**Archivos afectados:** ~9 archivos de frontend
**Riesgo:** ⚠️⚠️⚠️ Alto — afecta la UX directamente
**Mitigación:**
- Feature toggle para rollback rápido
- Tests E2E con Playwright
- Deploy progresivo (10% → 50% → 100%)

**Rollback:** Configurar feature toggle a `false`
**Tiempo estimado:** 2-4 semanas

---

## FASE 7 — Contract Tests

**Objetivo:** Asegurar que adapters cumplen contratos.

**Riesgo:** ❌ Bajo — solo se agregan tests
**Impacto:** Alto — previene regresiones en migración
**Tiempo estimado:** 3-5 días

### 7.1 Implementación

```python
# tests/contract/test_device_repository.py
import pytest
from typing import Protocol

from core.PHASE_1.domain.device.domain.entities import Device
from core.PHASE_1.domain.device.domain.repositories import DeviceRepository
from core.PHASE_1.domain.device.domain.value_objects import DeviceId, TenantId


class DeviceRepositoryContract(Protocol):
    """Contract que todo adapter debe cumplir."""

    async def save(self, device: Device) -> Result[Device, str]: ...
    async def get_by_id(self, device_id: DeviceId) -> Result[Device | None, str]: ...


class TestSQLAlchemyDeviceRepositoryContract:
    """Verifica que SQLAlchemy adapter cumple el contrato."""

    @pytest.fixture
    def repository(self) -> DeviceRepository:
        from apps.api.app.infrastructure.repositories.device import SQLAlchemyDeviceRepository
        return SQLAlchemyDeviceRepository(session)

    async def test_save_returns_ok_with_device(self, repository: DeviceRepository):
        device = Device.create(...)
        result = await repository.save(device)
        assert result.is_ok()
        assert isinstance(result.unwrap(), Device)

    async def test_get_by_id_returns_none_for_missing(self, repository: DeviceRepository):
        result = await repository.get_by_id(DeviceId.generate())
        assert result.unwrap() is None
```

### 7.2 Tests por contrato

| Contrato | Adapter | Tests |
|---|---|---|
| `DeviceRepository` | `SQLAlchemyDeviceRepository` | ~8 tests |
| `IncidentRepository` | `SQLAlchemyIncidentRepository` | ~8 tests |
| `KnowledgeRepository` | `SQLAlchemyKnowledgeRepository` | ~8 tests |
| `RecommendationRepository` | `SQLAlchemyRecommendationRepository` | ~8 tests |
| `AuthenticationProvider` | `SupabaseAuthProvider` | ~5 tests |
| `AuditProvider` | `DatabaseAuditProvider` | ~5 tests |

**Archivos afectados:** `tests/contract/`
**Riesgo:** ❌ Bajo
**Impacto:** Regression protection
**Rollback:** `git checkout HEAD -- tests/contract/`
**Tiempo estimado:** 3-5 días

---

## RESUMEN DEL ROADMAP

| Fase | Nombre | Riesgo | Tiempo | Dependencias |
|---|---|---|---|---|
| 0 | Baseline | Ninguno | 6 hr | Ninguna |
| 1 | Limpiar código muerto | Muy bajo | 5 hr | Ninguna |
| 2 | Composition Root | Medio | 3-5 días | FASE 1 |
| 3 | Unificar puertos | Medio-alto | 1-2 sem | FASE 2 |
| 4 | Mover infraestructura | ⚠️⚠️⚠️ Muy alto | 2-3 sem | FASE 3 + decidir PHASE_2 |
| 5 | PHASE_5 | Medio | 1 día - 3 sem | Decisión |
| 6 | Migrar frontend | ⚠️⚠️⚠️ Alto | 2-4 sem | FASE 2 + FASE 3 |
| 7 | Contract tests | Bajo | 3-5 días | FASE 3 |

**Total estimado:** 6-12 semanas para un equipo de 2 desarrolladores.

---

## PRIORIZACIÓN SUGERIDA

### Si el objetivo es estabilidad (corto plazo):
1. FASE 1 → FASE 2 → FASE 7 → FASE 5 (decidir) → PARAR

### Si el objetivo es arquitectura (medio plazo):
1. FASE 1 → FASE 2 → FASE 3 → FASE 7 → PARAR
2. Luego: FASE 4 (con PHASE_2 resuelto)

### Si el objetivo es escalabilidad (largo plazo):
1. FASE 1 → FASE 2 → FASE 3 → FASE 4 → FASE 5 → FASE 6 → FASE 7

---

*Documento de plan de migración. NO modifica código. Solo describe el roadmap.*
