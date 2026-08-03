# SHARED KERNEL — Elementos Transversales

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** Auditoría `docs/audit/DEAD_CODE_REPORT.md`

---

## PRINCIPIO FUNDADOR

> "Shared Kernel es el Subset del Dominio que dos o más Bounded Contexts acuerdan compartir. Es peligroso: acopla los Contexts que lo comparten."

No todo lo que "se usa en varios lugares" pertenece al Shared Kernel. Debe haber una justificación específica.

---

## REGLA DE INCLUSIÓN

Para cada elemento en `shared/` debe responderse:

> **"¿Por qué pertenece a más de un Bounded Context?"**

Si la respuesta es "porque se usa en varios lugares" sin más contexto, el elemento NO pertenece a shared/.

---

## ELEMENTOS VÁLIDOS EN SHARED/

### 1. Primitives de dominio

```python
shared/primitives/
├── entity_id.py      # EntityId — identidad transversal
├── aggregate_root.py # AggregateRoot — base class
├── value_object.py   # ValueObject — base class
└── domain_event.py  # DomainEvent — base class
```

**¿Por qué pertenece a más de un Context?**
Porque TODOS los Contexts necesitan identidad, agregados, value objects y eventos. Son primitivas del lenguaje de dominio.

**Evidencia de auditoría:** `core/PHASE_1/infrastructure/shared/primitives/` existe y es importado por todos los PHASEs. Esto valida la necesidad.

---

### 2. Result type

```python
shared/result/
├── result.py         # Result[T, E]
├── ok.py            # Ok[T]
└── err.py           # Err[E]
```

**¿Por qué pertenece a más de un Context?**
Porque TODOS los repositories y use cases de TODOS los Contexts retornan `Result[T, E]`. Es el tipo de retorno canónico del sistema.

**Justificación específica:**
- device usa `Result[Device, str]`
- clinical usa `Result[AIRecommendation, str]`
- ai usa `Result[EmbeddingVector, str]`
- audit usa `Result[AuditEntry, str]`

Si un Context no usa `Result`, no pertenece a este sistema arquitectónico.

**Evidencia de auditoría:** `core/PHASE_1/domain/device/domain/repositories/device_repository.py` define `Result[Device, str]`. Pero `apps/api/app/domain/device/repository.py` usa `DeviceModel | None` (sin Result). Hay dos sistemas incompatibles. La decisión arquitectónica es usar `Result` como estándar.

---

### 3. Errores base del sistema

```python
shared/errors/
├── domain_error.py    # DomainError base
├── repository_error.py # RepositoryError
├── application_error.py # ApplicationError
└── system_error.py    # SystemError (catastrófico)
```

**¿Por qué pertenece a más de un Context?**
Porque TODOS los Contexts pueden generar errores. Tener una jerarquía compartida permite manejo de errores consistente.

---

### 4. Tipos transversales muy básicos

```python
shared/types/
├── tenant_id.py       # TenantId — identidad de tenant
├── pagination.py      # Page, PageParams
└── maybe.py          # Maybe[T] — null safety
```

**¿Por qué pertenece a más de un Context?**
- `TenantId`: TODOS los Contexts operan en contexto de tenant
- `Page`, `PageParams`: TODAS las operaciones de list tienen paginación
- `Maybe[T]`: Operaciones que pueden no encontrar resultados son universales

---

## ELEMENTOS QUE NO PERTENECEN A SHARED/

### 1. Helpers y utilities

```python
# ❌ NO pertenece
shared/utils/helpers.py
shared/utils/date_utils.py
shared/utils/string_utils.py
```

**Razón:** Son utilities de programación, no conceptos de dominio. Cada Context puede tener sus propios helpers.

---

### 2. Constantes de negocio

```python
# ❌ NO pertenece
shared/constants/device_status.py
shared/constants/incident_priority.py
```

**Razón:** Son value objects que pertenecen a un Context específico. `DeviceStatus` pertenece a `device/`. Si otro Context necesita un status similar, define el suyo.

---

### 3. Clientes externos

```python
# ❌ NO pertenece
shared/clients/supabase_client.py
shared/clients/redis_client.py
```

**Razón:** Son infraestructura, no dominio. Pertenecen a `apps/{entry}/infrastructure/`.

---

### 4. Configuración

```python
# ❌ NO pertenece
shared/config/settings.py
shared/config/features.py
```

**Razón:** La configuración pertenece al entry point que la necesita. No es dominio.

---

## CASOS GRISES

### ¿ConversationId pertenece a shared/ o a ai/?

```
# Análisis:
# - ConversationId solo lo usa ai/ (sesiones de chat)
# - device/ no sabe qué es una ConversationId
# - clinical/ no sabe qué es una ConversationId
# - audit/ necesita referenciar ConversationId en logs
```

**Decisión: Pertenece a ai/ como value object.**

**Razón:** audit/ no necesita conocer el concepto de ConversationId — solo necesita referenciarlo como string. No hay necesidad de compartir el tipo.

**Evidencia de auditoría:** PHASE_2 tiene `session/` y `cognitive/session/` (duplicación). Si session es el contexto de ai/, no necesita vivir en shared/.

---

### ¿EventBus pertenece a shared/ o a infrastructure/?

```
# Análisis:
# - Event Bus es el mecanismo de publicación de Domain Events
# - device/ publica DeviceRegistered
# - clinical/ publica RecommendationGenerated
# - Todos los Contexts publican y subscriben eventos
```

**Decisión: El CONCEPTO de Event Bus pertenece a cada Context. La IMPLEMENTACIÓN pertenece a infrastructure.**

**Razón:** Cada Context define sus propios eventos de dominio. El bus que los distribuye es infraestructura. Los eventos como concepto (`DeviceRegistered`, `RecommendationGenerated`) son del dominio. El publisher/subscriber es infraestructura.

**Evidencia de auditoría:** `core/PHASE_1/infrastructure/events/` existe con EventBus, Publisher, Subscriber. Esto es infraestructura, no shared kernel. Los eventos (`DeviceRegistered`) sí son del dominio y viven en `device/domain/events/`.

---

## ESTRUCTURA PROPUESTA

```
core/shared/
├── primitives/
│   ├── entity_id.py
│   ├── aggregate_root.py
│   ├── value_object.py
│   └── domain_event.py
├── result/
│   ├── result.py
│   ├── ok.py
│   └── err.py
├── errors/
│   ├── domain_error.py
│   ├── repository_error.py
│   └── application_error.py
└── types/
    ├── tenant_id.py
    ├── pagination.py
    └── maybe.py
```

**Elementos actuales en auditoría que no están en shared/:**

| Elemento | Ubicación actual | ¿Pertenecer a shared/? |
|---|---|---|
| `Result[T, E]` | `core/PHASE_1/infrastructure/shared/result/` | ✅ Sí |
| Value objects base | `core/PHASE_1/infrastructure/shared/value_objects/` | ✅ Sí |
| Primitives | `core/PHASE_1/infrastructure/shared/primitives/` | ✅ Sí |
| Domain events base | `core/PHASE_1/infrastructure/shared/events/` | ✅ Sí |
| `DeviceId`, `TenantId` | `core/PHASE_1/domain/device/domain/value_objects/` | ❌ No — pertenece a device/ |

---

## GOBIERNO DE SHARED/

El Shared Kernel cambia lentamente. Cada modificación requiere:

1. Justificación explícita: "¿Por qué este cambio afecta a más de un Context?"
2. Verificación de que TODOS los Contexts que lo consumen compilan después del cambio
3. Contract tests que fallen si un Context rompe la compatibilidad

**Evidencia de auditoría:** Los value objects en `core/PHASE_1/infrastructure/shared/` son usados por PHASE_2, PHASE_3, PHASE_4. Cambios en shared/ pueden romper múltiples Contexts simultáneamente.

---

## REGLA DE LIMPIEZA

Si un elemento en `shared/` solo es usado por un Context después de 6 meses, se mueve a ese Context.

```bash
# Verificar uso de cada elemento en shared/
for file in core/shared/**/*.py; do
    contexts=$(grep -rl "from core.shared.${file%.py}" core/*/ | wc -l)
    if [ $contexts -eq 1 ]; then
        echo "MOVE: $file (used by only one context)"
    fi
done
```

**Evidencia de auditoría:** `shared/` actualmente vive en `core/PHASE_1/infrastructure/shared/`. Si el shared kernel se mueve a `core/shared/`, los 6 meses se cuentan desde ese momento.

---

*El Shared Kernel es la parte más frágil de la arquitectura. Cambiar con extrema precaución.*
