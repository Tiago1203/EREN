# EREN OS Naming Conventions

**Fecha:** 2026-07-14  
**Versión:** 1.0

---

## 1. CONVENCIONES GENERALES

### 1.1 Reglas de Oro

1. **Clarity over brevity**: `get_user_by_id` > `get_user`
2. **Descriptive over vague**: `pending_tasks_count` > `count`
3. **Consistent over creative**: Mantener patrones existentes

### 1.2 Nomenclatura Universal

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Clase | PascalCase | `CognitiveEngine` |
| Interface | PascalCase + Sufijo | `EnginePort`, `StorageContract` |
| Protocol | PascalCase + Sufijo | `CognitiveEngineProtocol` |
| Exception | PascalCase + Sufijo | `ValidationError` |
| Enum | PascalCase | `EngineStatus` |
| Enum Value | UPPER_SNAKE | `STATUS_RUNNING` |
| Function | snake_case | `create_engine` |
| Method | snake_case | `get_metrics` |
| Variable | snake_case | `user_id` |
| Constant | UPPER_SNAKE | `MAX_RETRIES` |
| Module | snake_case | `event_bus.py` |
| Package | snake_case | `core/events` |
| Private Method | _snake_case | `_internal_method` |
| Private Variable | _snake_case | `_cache` |

---

## 2. NOMBRES DE ARCHIVOS

### 2.1 Patrón: `{feature}_{type}.py`

| Tipo | Sufijo | Ejemplo |
|------|--------|---------|
| Engine | `_engine.py` | `memory_engine.py` |
| Manager | `_manager.py` | `session_manager.py` |
| Factory | `_factory.py` | `engine_factory.py` |
| Validator | `_validator.py` | `dependency_validator.py` |
| Exceptions | `_exceptions.py` | `container_exceptions.py` |
| Events | `_events.py` | `boot_events.py` |
| Metrics | `_metrics.py` | `reasoning_metrics.py` |
| Types | `_types.py` | `orchestration_types.py` |
| Models | `_models.py` | `workflow_models.py` |
| Interfaces | `_interfaces.py` | `capability_interfaces.py` |
| Registry | `_registry.py` | `provider_registry.py` |

### 2.2 Archivos Especiales

| Archivo | Propósito |
|---------|----------|
| `__init__.py` | Exports públicos del módulo |
| `__all__.py` | Lista de exports públicos |
| `exceptions.py` | Todas las excepciones del módulo |
| `types.py` | Todos los tipos del módulo |
| `models.py` | Todos los modelos del módulo |
| `events.py` | Todos los eventos del módulo |
| `metrics.py` | Todas las métricas del módulo |

---

## 3. NOMBRES DE CLASES

### 3.1 Sufijos Estándar

| Sufijo | Uso | Ejemplo |
|--------|-----|---------|
| `Engine` | Motores de procesamiento | `ReasoningEngine` |
| `Platform` | Sistemas complejos | `ReasoningPlatform` |
| `Manager` | Gestión de recursos | `SessionManager` |
| `Registry` | Registro de servicios | `CapabilityRegistry` |
| `Factory` | Creación de objetos | `EngineFactory` |
| `Builder` | Construcción paso a paso | `PipelineBuilder` |
| `Validator` | Validación | `InputValidator` |
| `Coordinator` | Coordinación | `MemoryCoordinator` |
| `Handler` | Manejo de eventos | `EventHandler` |
| `Processor` | Procesamiento | `DataProcessor` |
| `Collector` | Recolección | `MetricsCollector` |
| `Publisher` | Publicación | `EventPublisher` |
| `Subscriber` | Suscripción | `EventSubscriber` |

### 3.2 Prefijos Estándar

| Prefijo | Uso | Ejemplo |
|---------|-----|---------|
| `Base` | Clase base | `BaseEngine` |
| `Abstract` | Clase abstracta | `AbstractProcessor` |
| `Internal` | Interno | `InternalCache` |
| `Mock` | Para testing | `MockProvider` |

---

## 4. NOMBRES DE CONTRATOS

### 4.1 Contratos de Plataforma

| Contrato | Nombre | Ejemplo |
|----------|--------|---------|
| Motor cognitivo | `{Name}Contract` | `MemoryContract` |
| Capacidad | `{Name}Port` | `RetrievalPort` |
| Servicio | `{Name}Service` | `LoggingService` |

### 4.2 Nomenclatura de Contratos

```
contracts/
├── base.py              # CognitiveEngine, SupportsLifecycle
├── memory.py            # Memory contract
├── reasoning.py         # Reasoning contract
├── planning.py          # Planner contract
├── workflow.py         # Workflow contract
├── knowledge.py        # Knowledge contract
├── diagnostic.py       # Diagnostic contract
└── tool.py             # Tool contract
```

---

## 5. VARIABLES Y PARÁMETROS

### 5.1 Nombres de Variables

```python
# ❌ MAL
x = get_users()
d = {}
cnt = 0

# ✅ BIEN
users = get_users()
user_database = {}
active_count = 0
```

### 5.2 Nombres de Parámetros

```python
def create_engine(
    name: str,                    # Entidad
    config: dict,                  # Configuración
    timeout: int = 30,             # Configuración con default
    max_retries: int = MAX_RETRIES,  # Constante
) -> Engine:                      # Tipo de retorno
    ...
```

---

## 6. CONSTANTES

### 6.1 Naming de Constantes

```python
# Estados
class EngineStatus:
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

# Límites
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
MAX_BATCH_SIZE = 1000

# Prefijos
PREFIX_CAPABILITY = "capability:"
PREFIX_SESSION = "session:"
```

---

## 7. EVENTOS

### 7.1 Naming de Eventos

```python
class EventType:
    # Estructura: {NOUN}_{VERBED}
    ENGINE_CREATED = "engine_created"
    ENGINE_STARTED = "engine_started"
    ENGINE_STOPPED = "engine_stopped"
    ENGINE_ERROR = "engine_error"
    
    TASK_SUBMITTED = "task_submitted"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
```

---

## 8. EXCEPCIONES

### 8.1 Naming de Excepciones

```python
# Estructura: {Context}{ErrorType}

class ERENError(Exception):
    """Base exception for EREN."""
    pass

class ValidationError(ERENError):
    """Raised when validation fails."""
    pass

class ConfigurationError(ERENError):
    """Raised when configuration is invalid."""
    pass

class ResourceNotFoundError(ERENError):
    """Raised when resource is not found."""
    pass

class ServiceError(ERENError):
    """Raised when a service operation fails."""
    pass
```

---

## 9. TESTS

### 9.1 Naming de Tests

```python
class TestEngineCreation:
    """Tests for Engine creation."""
    
    def test_creates_engine_with_valid_config(self):
        """Should create engine when config is valid."""
        ...
    
    def test_raises_error_for_invalid_config(self):
        """Should raise error when config is invalid."""
        ...
    
    def test_returns_correct_engine_type(self):
        """Should return correct engine subclass."""
        ...
```

---

## 10. CHECKLIST

- [ ] ¿El nombre es descriptivo?
- [ ] ¿Sigue las convenciones de PascalCase/snake_case?
- [ ] ¿Usa sufijos estándar (Engine, Manager, etc.)?
- [ ] ¿Evita abreviaciones no estándar?
- [ ] ¿Es consistente con el resto del código?

---

*Architecture Review Board*
