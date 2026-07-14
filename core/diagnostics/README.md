# core/diagnostics - Sistema de Diagnóstico

## Descripción

El sistema de **Diagnostics** proporciona validación completa del sistema EREN OS.

## Responsabilidad

- Auditar el Composition Root
- Validar dependencias
- Verificar contratos
- Generar reportes de salud

## Arquitectura

```
Diagnostics Engine
    │
    ├── Architecture Validator
    ├── Contract Validator
    ├── Dependency Validator
    ├── Runtime Validator
    ├── Health Checker
    └── Report Generator
```

## Uso

```python
from core.diagnostics import ERENDiagnostics

report = ERENDiagnostics().run_full_system_validation()
print(report.score)
```

## Límites

- **Puede depender de:** todos los módulos core
- **Nunca depende de:** apps

---
*Architecture only - no business logic*
