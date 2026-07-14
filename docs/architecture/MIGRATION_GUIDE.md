# EREN OS Migration Guide

**Fecha:** 2026-07-14  
**Versión:** 2.0  
**Estado:** Guía de Migración

---

## 1. MIGRACIONES REQUERIDAS

### 1.1 Merge workflow/ → workflows/

**Problema:** workflow/ es un stub redundante.

**Acción:** Mover contenido de workflow/ a workflows/.

**Impacto:** Breaking change para imports.

**Antes:**
```python
from core.workflow import WorkflowEngine
```

**Después:**
```python
from core.workflows import WorkflowEngine
```

**Aliases para backwards compatibility:**
```python
# core/workflow/__init__.py
from core.workflows import *
import warnings
warnings.warn("core.workflow is deprecated, use core.workflows", DeprecationWarning)
```

---

### 1.2 Deprecate diagnostic/

**Problema:** diagnostic/ es un stub con 6 archivos.

**Acción:** Re-exportar desde diagnostics/.

**Antes:**
```python
from core.diagnostic import DiagnosticEngine
```

**Después:**
```python
from core.diagnostics import DiagnosticEngine
```

---

### 1.3 Fix Memory Exports

**Problema:** Tipos importados de dos fuentes.

**Acción:** Elegir fuente canónica.

**Antes:**
```python
from core.memory import MemoryEntry  # ambiguous
```

**Después:**
```python
# Canónica: memory_models.py
from core.memory.memory_models import MemoryEntry
```

---

## 2. MIGRACIONES OPCIONALES

### 2.1 Estandarizar Nombres de Archivos

| Actual | Recomendado |
|--------|-------------|
| boot_events.py | boot_events.py ✅ |
| scheduling_events.py | scheduler_events.py |
| runtime_events.py | runtime_events.py ✅ |

---

## 3. BREAKING CHANGES

### 3.1 Lista de Breaking Changes

| Cambio | Severidad | Workaround |
|--------|----------|------------|
| workflow/ → workflows/ | MEDIA | Usar alias |
| diagnostic/ → diagnostics/ | BAJA | Usar alias |

---

## 4. ROLLBACK PLAN

Si algo falla:

```bash
git revert <commit>
```

---

*Architecture Review Board*
