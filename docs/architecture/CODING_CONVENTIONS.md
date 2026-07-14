# EREN OS Coding Conventions

**Fecha:** 2026-07-14  
**Versión:** 1.0

---

## 1. PRINCIPIOS GENERALES

### 1.1 Filosofía

> "El código se escribe una vez, se lee muchas veces."

- Prioriza claridad sobre clever
- Prioriza simplicidad sobre complejidad
- Prioriza mantenibilidad sobre optimización prematura

### 1.2 Reglas de Oro

1. **Regla del Boy Scout**: Deja el código más limpio de como lo encontraste
2. **Regla de los 3**: Si vas a repetir algo 3 veces, abstrae
3. **Regla YAGNI**: No implementes features que no necesitas

---

## 2. PRINCIPIOS SOLID

### 2.1 Single Responsibility (SRP)

**Regla:** Cada clase tiene una única razón para cambiar.

```python
# ❌ MAL - Múltiples razones para cambiar
class UserManager:
    def authenticate(self): ...
    def save_to_database(self): ...
    def send_email(self): ...
    def generate_report(self): ...

# ✅ BIEN - Responsabilidad única
class Authenticator:
    def authenticate(self): ...

class UserRepository:
    def save(self): ...

class EmailService:
    def send(self): ...
```

### 2.2 Open/Closed (OCP)

**Regla:** Abierto para extensión, cerrado para modificación.

```python
# ❌ MAL - Modificar para agregar nuevos tipos
def process(item):
    if item.type == "pdf":
        ...
    elif item.type == "doc":
        ...

# ✅ BIEN - Extender sin modificar
class Processor(ABC):
    @abstractmethod
    def process(self, item): ...

class PDFProcessor(Processor):
    def process(self, item): ...

class DOCProcessor(Processor):
    def process(self, item): ...
```

### 2.3 Liskov Substitution (LSP)

**Regla:** Objetos de subclase deben poder sustituir objetos de la clase padre.

```python
# ❌ MAL - Violación de LSP
class Rectangle:
    def set_width(self, w): ...
    def set_height(self, h): ...

class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w  # Violación!

# ✅ BIEN - Contrato claro
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...
```

### 2.4 Interface Segregation (ISP)

**Regla:** Preferir muchas interfaces específicas sobre una general.

```python
# ❌ MAL - Interface grande
class IMachine(ABC):
    def print(self): ...
    def scan(self): ...
    def fax(self): ...

# ✅ BIEN - Interfaces pequeñas
class IPrinter(ABC):
    @abstractmethod
    def print(self): ...

class IScanner(ABC):
    @abstractmethod
    def scan(self): ...
```

### 2.5 Dependency Inversion (DIP)

**Regla:** Depender de abstracciones, no de concreciones.

```python
# ❌ MAL - Depende de concreción
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()  # Concreto!

# ✅ BIEN - Depende de abstracción
class OrderService:
    def __init__(self, db: Database):
        self.db = db  # Abstraction!
```

---

## 3. REGLAS DE CÓDIGO

### 3.1 Nombres

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Clase | PascalCase | `CognitiveEngine` |
| Función | snake_case | `create_engine` |
| Constante | UPPER_SNAKE | `MAX_RETRIES` |
| Variable | snake_case | `user_id` |
| Módulo | snake_case | `event_bus.py` |
| Package | snake_case | `core/events` |

### 3.2 Longitud

| Elemento | Máximo | Recomendado |
|----------|--------|-------------|
| Función | 50 líneas | < 20 |
| Clase | 300 líneas | < 150 |
| Archivo | 500 líneas | < 300 |
| Método | 20 líneas | < 10 |

### 3.3 Imports

```python
# 1. Standard library
import os
import sys
from typing import Optional

# 2. Third party
import pydantic

# 3. Internal - absolute
from core.events import EventBus

# 4. Internal - relative (solo cuando necesario)
from .models import User

# ❌ Evitar
from core.events import *
```

### 3.4 Docstrings

```python
def create_engine(name: str, config: dict) -> Engine:
    """Create a cognitive engine.

    Args:
        name: Unique name for the engine.
        config: Configuration dictionary.

    Returns:
        A configured Engine instance.

    Raises:
        EngineCreationError: If engine creation fails.

    Example:
        >>> engine = create_engine("reasoning", {"timeout": 30})
        >>> engine.start()
    """
    ...
```

---

## 4. PATRONES DE DISEÑO

### 4.1 Patrones Recomendados

| Patrón | Uso |
|--------|-----|
| Factory | Crear instancias complejas |
| Registry | Registrar y descubrir servicios |
| Strategy | Intercambiar algoritmos |
| Observer | Notificar cambios |
| Builder | Construir objetos complejos |
| Adapter | Integrar interfaces incompatibles |

### 4.2 Patrones a Evitar

| Patrón | Razón |
|--------|-------|
| Singleton | Dificulta testing |
| Global State | Acoplamiento oculto |
| God Object | Violación de SRP |

---

## 5. MANEJO DE ERRORES

### 5.1 Excepciones

```python
# ✅ BIEN - Excepciones específicas
class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class EngineNotFoundError(ValidationError):
    """Raised when engine is not found in registry."""
    pass

# ❌ MAL - Excepciones genéricas
raise Exception("Something went wrong")
```

### 5.2 Try/Except

```python
# ✅ BIEN
try:
    result = service.process(data)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    raise
except ServiceError as e:
    logger.warning(f"Service error: {e}")
    return fallback()

# ❌ MAL
try:
    result = service.process(data)
except:
    pass  # Silenciar errores!
```

---

## 6. TESTING

### 6.1 Naming

```python
class TestEngineCreation:
    def test_creates_engine_with_valid_config(self): ...
    def test_raises_error_for_invalid_config(self): ...
    def test_returns_correct_engine_type(self): ...
```

### 6.2 Estructura

```python
class TestMyClass:
    def setup_method(self):
        """Setup for each test."""
        self.sut = MyClass()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.sut.dispose()
    
    def test_behavior_one(self):
        # Arrange
        input_data = ...
        
        # Act
        result = self.sut.process(input_data)
        
        # Assert
        assert result == expected
```

---

## 7. DOCUMENTACIÓN

### 7.1 README de Módulo

```markdown
# Module Name

## Descripción
[1-2 párrafos]

## Responsabilidad
[Qué hace el módulo]

## Uso
```python
[Ejemplo]
```

## Límites
- Puede depender de: [lista]
- Nunca depende de: [lista]
```

---

*Architecture Review Board*
