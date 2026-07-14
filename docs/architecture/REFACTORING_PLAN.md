# EREN OS Refactoring Plan

**Date:** 2026-07-14  
**Based on:** Architecture Audit Report v1.0  
**Status:** PENDING APPROVAL

---

## Overview

Este plan de refactorización está basado en el Architecture Audit Report y propone cambios estructurados en fases para mejorar la calidad del código sin romper funcionalidad existente.

## Guiding Principles

1. **No romper backwards compatibility** sin justificación clara
2. **Cambios incrementales** que puedan revertirse
3. **Tests primero** - cada refactor debe tener tests
4. **Documentar decisiones** en ADRs

---

## Phase 1: Critical Fixes (Week 1-2)

### 1.1 Fix Memory Exports Duplication [CRITICAL]

**Problem:** `core/memory/__init__.py` importa `MemoryEntry`, `MemoryQuery`, `MemoryType` dos veces.

**Current State:**
```python
# Líneas 34-43
from core.memory.memory_models import (
    MemoryEntry,
    MemoryQuery,
    MemoryType,
    ...
)

# Líneas 91-101
from core.memory.types import (
    MemoryType,  # DUPLICADO
    MemoryState,
    ...
)
```

**Solution:**
1. Elegir una fuente canónica para cada tipo
2. Mover tipos a `memory_models.py` o `memory_types.py`
3. Crear aliases para backwards compatibility
4. Eliminar imports duplicados

**Files to modify:**
- `core/memory/__init__.py`

**Risk:** MEDIUM - Aliases mantendrán backwards compatibility

**Verification:**
```bash
pytest tests/unit/core/memory/ -v
```

---

### 1.2 Fix Failing Test [CRITICAL]

**Problem:** `test_event_publisher_disabled_without_bus` falla.

**Current behavior:**
```python
assert not publisher._enabled  # Falla porque _enabled = True
```

**Expected behavior:** `_enabled` debería ser `False` por defecto.

**Root cause:** El publisher se inicializa con el bus global activo.

**Solution options:**
1. Modificar el test para reflejar comportamiento real
2. Modificar el publisher para que _enabled=False por defecto

**Recommendation:** Opción 1 - el test tenía asunción incorrecta.

**Files to modify:**
- `tests/unit/core/reasoning/test_hardening.py`

**Risk:** LOW

**Verification:**
```bash
pytest tests/unit/core/reasoning/test_hardening.py -v
```

---

### 1.3 Add Missing Dependencies [HIGH]

**Problem:** `pydantic` y `pytest-asyncio` no están documentados.

**Current state:** Se descubrieron al ejecutar tests.

**Solution:**
1. Verificar `requirements.txt` o `pyproject.toml`
2. Agregar dependencias faltantes
3. Agregar a CI/CD

**Files to create/modify:**
- `requirements.txt` (crear si no existe)
- `pyproject.toml` (agregar si falta)

**Content:**
```txt
# Core
pydantic>=2.0,<3.0

# Testing
pytest>=8.0
pytest-asyncio>=0.23
pytest-cov>=4.0
```

**Risk:** NONE

---

### 1.4 Verify All Tests Run [HIGH]

**Problem:** 13 errores de colección en pytest.

**Root cause:** Módulos no encontrados o imports rotos.

**Solution:**
1. Ejecutar `pytest --collect-only` para identificar problemas
2. Fix individual de cada módulo
3. Agregar a CI/CD

**Verification:**
```bash
pytest --collect-only 2>&1 | grep -c "error"
# Should be 0
```

---

## Phase 2: Architecture Cleanup (Week 2-4)

### 2.1 Consolidate workflow/ into workflows/ [HIGH]

**Problem:** `core/workflow/` (5 archivos) y `core/workflows/` (14 archivos) causan confusión.

**Current State:**
```
core/workflow/    → "scaffolding only" (5 archivos stubs)
core/workflows/   → "full platform" (14 archivos)
```

**Solution Options:**

**Option A: Merge (Recommended)**
1. Mover contenido de `workflow/` a `workflows/`
2. Hacer `workflow/` un thin wrapper que re-exporta desde `workflows/`
3. Agregar deprecation warning a `workflow/`

**Option B: Rename**
1. Renombrar `workflow/` a `workflow-stubs/`
2. Mantener `workflows/` como está

**Recommendation:** Option A

**Files to modify:**
- `core/workflow/__init__.py` → re-export from workflows/
- `core/workflow/engine.py` → wrapper
- `core/workflow/README.md` → deprecation notice

**Files to add:**
- `core/workflows/DEPLOYMENT_STRATEGY.md`

**Risk:** MEDIUM

**Verification:**
```bash
# Old import still works
python -c "from core.workflow import WorkflowEngine"
# New import works
python -c "from core.workflows import WorkflowEngine"
```

---

### 2.2 Clarify planning/ vs planner/ [HIGH]

**Problem:** Dos módulos con nombres similares pero diferentes propósitos.

**Current State:**
```
core/planner/    → contratos, interfaces, stubs (11 archivos)
core/planning/   → implementación completa (12 archivos)
```

**Solution:**
1. Documentar en ARCHITECTURE_DECISION.md
2. Agregar `__init__.py` exports claros
3. Mantener ambos - cumplen propósitos diferentes

**Documentation needed:**
```markdown
## Decision: Why two planning modules?

### core/planner/
- Propósito: Contratos e interfaces mínimas
- Uso: Dependencias de otros módulos
- Contenido: Interfaces, tipos base, stubs

### core/planning/
- Propósito: Implementación completa
- Uso: Lógica de negocio
- Contenido: Engines, algoritmos, etc.
```

**Files to create:**
- `docs/adr/ADR-002-planning-modules.md`

**Risk:** NONE

---

### 2.3 Add Missing READMEs [HIGH]

**Problem:** 6 módulos sin README dedicado.

**Modules needing READMEs:**
1. `core/boot/` - Boot Manager
2. `core/composition/` - Composition Root
3. `core/container/` - DI Container
4. `core/context/` - Context Manager
5. `core/orchestration/` - Orchestration Contracts

**Template for each README:**
```markdown
# [Module Name]

## Overview
[1-2 paragraphs]

## Architecture
```
[Simple diagram]
```

## Components
| Component | Purpose |
|-----------|---------|

## Usage
```python
[Basic example]
```

## Integration
```
[How it connects to other modules]
```

## Boundaries
- May depend on: [list]
- Never depends on: [list]
```

**Risk:** NONE

---

## Phase 3: Refinement (Week 4-6)

### 3.1 Reduce Memory Exports [MEDIUM]

**Problem:** ~70 exports en `core/memory/__init__.py` hace difícil de usar.

**Current exports:**
```python
~70 symbols including:
- 10+ stores
- 15+ types
- 20+ exceptions
- 10+ components
```

**Solution:**
1. Crear "public API" reducida (~20 symbols)
2. Mantener todos los exports actuales como aliases
3. Agregar deprecation warnings a exports "internals"
4. Documentar qué es público vs interno

**Proposed Public API:**
```python
# Solo estos son "públicos"
__all__ = [
    # Core Engine
    "CognitiveMemoryEngine",
    # Main types
    "MemoryEntry",
    "MemoryType",
    "MemoryQuery",
    # Stores
    "MemoryStore",
    "WorkingMemoryStore",
    # Coordinator
    "MemoryCoordinator",
    "get_memory_coordinator",
    # Registry
    "MemoryRegistry",
    "get_memory_registry",
    # Main exceptions
    "MemoryError",
    "MemoryNotFoundError",
]
```

**Files to modify:**
- `core/memory/__init__.py`

**Risk:** MEDIUM - Deprecation warnings necesarios

---

### 3.2 Improve Boot Manager Type Safety [MEDIUM]

**Problem:** `_create_*` methods retornan diccionarios en lugar de interfaces.

**Current:**
```python
def _create_event_bus(self):
    return {"type": "event_bus", "interface": "EventPublisher"}  # Dict!
```

**Solution:**
1. Crear protocolo `BootComponent`
2. Retornar instancias del protocolo
3. Mantener backwards compatibility con dict

**Files to modify:**
- `core/boot/boot_manager.py`
- `core/boot/boot_types.py` (agregar protocolo)

**Risk:** MEDIUM

---

### 3.3 Standardize Naming [LOW]

**Problem:** Pequeñas inconsistencias en naming.

**Inconsistencies:**
- `X` vs `XEngine` para algunos módulos
- Mezcla de `Platform` y no `Platform` suffix

**Solution:**
1. No cambiar nada - inconsistencias son menores
2. Documentar convenciones actuales

**Files to create:**
- `docs/CODING_CONVENTIONS.md`

**Risk:** NONE

---

## Phase 4: Validation (Week 6-7)

### 4.1 Run Full Test Suite

```bash
pytest tests/ -v --tb=short
```

**Expected:** 100% passing

### 4.2 Run Coverage Analysis

```bash
pytest tests/ --cov=core --cov-report=html
```

**Target:** >80% coverage

### 4.3 Performance Benchmarks

```bash
python -m pytest tests/ --durations=10
```

**Target:** No regression en tiempos

---

## Rollback Plan

Si cualquier refactor causa problemas:

1. **Git revert** del commit problemático
2. **Documentar** el rollback en el ADR
3. **Run tests** para verificar rollback
4. **Comunicar** al equipo

---

## Success Criteria

| Criteria | Target | Measurement |
|----------|--------|-------------|
| Test pass rate | 100% | `pytest --tb=short` |
| Coverage | >80% | `pytest --cov` |
| Docs complete | 100% | README count |
| No circular deps | TRUE | `pydeps --cycle` |
| Type hints | >90% | `mypy` |

---

## Timeline

```
Week 1: Phase 1 (Critical Fixes)
├── 1.1 Memory exports fix
├── 1.2 Fix failing test
├── 1.3 Add dependencies
└── 1.4 Verify tests run

Week 2-3: Phase 2 (Architecture Cleanup)
├── 2.1 Consolidate workflow/
├── 2.2 Clarify planning/
└── 2.3 Add READMEs

Week 4-5: Phase 3 (Refinement)
├── 3.1 Reduce Memory exports
├── 3.2 Improve type safety
└── 3.3 Standardize naming

Week 6-7: Phase 4 (Validation)
├── 4.1 Full test suite
├── 4.2 Coverage analysis
└── 4.3 Performance benchmarks
```

---

## Open Questions

1. **workflow/ vs workflows/**: ¿Option A (merge) o Option B (rename)?
2. **Memory exports**: ¿Cuántos symbols son realmente necesarios públicos?
3. **Naming**: ¿Cambiar naming o documentar convenciones actuales?

---

## Appendix: Files to Modify

### Phase 1
- `core/memory/__init__.py`
- `tests/unit/core/reasoning/test_hardening.py`
- `requirements.txt` or `pyproject.toml`

### Phase 2
- `core/workflow/__init__.py`
- `core/workflow/README.md`
- `docs/adr/ADR-002-planning-modules.md`
- `core/boot/README.md` (new)
- `core/composition/README.md` (new)
- `core/container/README.md` (new)
- `core/context/README.md` (new)
- `core/orchestration/README.md` (new)

### Phase 3
- `core/memory/__init__.py` (update)
- `core/boot/boot_manager.py`
- `core/boot/boot_types.py`
- `docs/CODING_CONVENTIONS.md` (new)

---

**End of Plan**

*Awaiting approval to proceed with Phase 1*
