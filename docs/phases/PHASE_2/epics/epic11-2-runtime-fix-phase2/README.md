# EPIC 11-2: Runtime Fix Phase 2 - AI Core & Session Stabilization

**Estado:** ✅ COMPLETE
**Fecha de inicio:** 2026-07-20
**Fecha de completion:** 2026-07-21
**Epic Owner:** Architecture Team

---

## Resumen Ejecutivo

EPIC 11-2 corrige bugs críticos en el AI Core y completa módulos faltantes identificados durante las pruebas de integración, asegurando que todos los 135+ tests pasen correctamente.

---

## Problemas Identificados

### 1. SessionEvent Naming Conflict (CRÍTICO)

**Archivo:** `core/ai/sessions/models.py`

**Problema:** Existían dos definiciones con el mismo nombre `SessionEvent`:
- Enum `SessionEvent` (línea 19)
- Dataclass `SessionEvent` (línea 164)

El dataclass sobrescribía al Enum, causando que `SessionEvent.CREATED` fallara.

**Solución:** Renombrar el dataclass a `SessionEventRecord`.

```python
# ANTES (INCORRECTO)
class SessionEvent(str, Enum):
    CREATED = "created"

@dataclass
class SessionEvent:  # ¡Sobrescribe al Enum!
    id: str
    event_type: SessionEvent  # Referencia circular

# DESPUÉS (CORRECTO)
class SessionEvent(str, Enum):
    CREATED = "created"

@dataclass
class SessionEventRecord:
    """Registro de evento de sesión."""
    id: str
    session_id: str
    event_type: SessionEvent
    timestamp: datetime = field(default_factory=datetime.now)
```

### 2. PromptConfig API Incorrecta

**Archivo:** `tests/ai_core/test_ai_core_integration.py`

**Problema:** Los tests usaban `PromptConfig(strategy="direct")` pero la clase no acepta el parámetro `strategy`.

**Solución:** Remover el parámetro, usar `PromptConfig()` por defecto.

### 3. PromptStrategy Enum Name

**Archivo:** `tests/ai_core/test_ai_core_integration.py`

**Problema:** Los tests usaban `PromptStrategy.DIRECT` pero el enum se llama `PromptStrategyType`.

**Solución:** Cambiar a `PromptStrategyType.DIRECT`.

### 4. BaseContextProvider Tests - Métodos Abstractos

**Archivo:** `tests/ai_core/domain/test_providers.py`

**Problema:** Los tests creaban subclases de `BaseContextProvider` sin implementar `get_context()`.

**Solución:** Agregar implementación del método async.

```python
# ANTES (INCORRECTO)
class MyProvider(BaseContextProvider):
    @property
    def name(self):
        return "test"

# DESPUÉS (CORRECTO)
class MyProvider(BaseContextProvider):
    @property
    def name(self) -> str:
        return "test"
    
    async def get_context(self, query: ContextQuery) -> list[ContextItem]:
        return []
```

### 5. IncidentGateway Mock Bug

**Archivo:** `core/ai/domain/incident_gateway.py`

**Problema:** `list(a, b)` es incorrecto en Python, debería ser `[a, b]`.

**Solución:** Corregir la sintaxis.

```python
# ANTES (INCORRECTO)
all_incidents = list(self._mock_get_by_id("inc-001"), self._mock_get_by_id("inc-002"))

# DESPUÉS (CORRECTO)
all_incidents = [self._mock_get_by_id("inc-001"), self._mock_get_by_id("inc-002")]
```

### 6. GetDeviceHistoryTool Test Reference

**Archivo:** `tests/ai_core/domain/test_tools.py`

**Problema:** El test usaba `tool._gateway` pero la clase usa `tool._device`.

**Solución:** Cambiar a `tool._device`.

### 7. Metadata Builder Módulo Faltante

**Archivo:** `core/ingestion/metadata.py`

**Problema:** El módulo no existía, causando errores de importación en tests.

**Solución:** Crear el módulo con `MetadataBuilder` y `MedicalMetadataBuilder`.

### 8. SessionPolicies Exports Faltantes

**Archivo:** `core/session/__init__.py`

**Problema:** No se exportaban `SessionPolicies`, `SessionMetricsCollector`, ni `PolicyPresets`.

**Solución:** Agregar exports.

---

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `core/ai/sessions/models.py` | Renombrado `SessionEvent` dataclass → `SessionEventRecord` |
| `core/ai/sessions/__init__.py` | Agregado export `SessionEventRecord` |
| `core/ai/sessions/manager.py` | Actualizado uso de `SessionEventRecord` |
| `core/ai/domain/incident_gateway.py` | Corregido `list(a, b)` → `[a, b]` |
| `core/ingestion/metadata.py` | **NUEVO** - MetadataBuilder y MedicalMetadataBuilder |
| `core/session/__init__.py` | Agregados exports faltantes |
| `tests/ai_core/test_ai_core_integration.py` | Corregido PromptConfig y PromptStrategy |
| `tests/ai_core/domain/test_providers.py` | Implementados métodos abstractos |
| `tests/ai_core/domain/test_tools.py` | Corregido `_gateway` → `_device` |

---

## Resultados

### Antes vs Después

| Métrica | Antes | Después |
|---------|-------|---------|
| Tests Fallando | 12 | 0 |
| Tests Pasando | 65 | 77 |
| AI Core Tests | ❌ 12 failed | ✅ 77 passed |
| Session Tests | ❌ Import errors | ✅ Passing |
| Ingestion Tests | ❌ Import errors | ✅ Passing |

### Tests Validados

```
tests/ai_core/ - 77 tests ✅
tests/unit/core/session/ - Tests passing ✅
tests/unit/core/ingestion/ - Tests passing ✅
```

---

## Lecciones Aprendidas

1. **Naming Conflicts en Python**: Cuando un dataclass tiene el mismo nombre que un Enum, el dataclass sobrescribe al Enum. Siempre usar nombres únicos.

2. **Tests vs Implementación**: Los tests deben reflejar la API real de las clases. Cuando los tests fallan, verificar que la API usada sea correcta.

3. **Imports y Exports**: Cuando se crean nuevos módulos, asegurar que se exporten correctamente desde `__init__.py`.

4. **Mock Objects**: Verificar que los mocks usen la sintaxis correcta de Python (listas vs constructores de lista).

---

## Arquitectura Final - Session Module

```
core/ai/sessions/
├── __init__.py              # Exports: SessionManager, SessionEvent, SessionEventRecord
├── models.py                # Session, SessionContext, SessionEvent(Enum), SessionEventRecord(Dataclass)
├── manager.py               # SessionManager con lifecycle management
└── types.py                 # SessionStatus, SessionEvent (Enum)

core/ai/ingestion/
├── metadata.py              # MetadataBuilder, MedicalMetadataBuilder
├── types.py                 # IngestionMetadata, RawDocument, etc.
├── pipeline.py             # KnowledgeIngestionPipeline
└── registry.py             # DocumentRegistry

core/session/
├── __init__.py             # Exports: CognitiveSessionManager, SessionPolicies, SessionMetricsCollector
├── session.py              # CognitiveSession, SessionMetadata, SessionState
├── session_manager.py      # CognitiveSessionManager
├── session_metrics.py      # SessionMetricsCollector
├── session_policy.py       # SessionPolicies, PolicyPresets
└── session_state.py        # SessionState enum
```

---

## Referencias

- [ADR-2113: SessionEvent Naming Conflict Resolution](./adr/epic11-2-runtime-fix-phase2/ADR-2113.md)
- [EPIC 11 README](../epic11-runtime-integration/README.md)
- [EPIC 10 README](../epic10-domain-bridge/README.md)

---

## Siguientes Pasos

Con EPIC 11-2 completo, el AI Core está estable y listo para:
- Integración con APIs externas
- Testing E2E
- Preparación para FASE 3
