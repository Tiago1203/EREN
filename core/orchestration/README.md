# core/orchestration - Orchestration Contracts

## Descripción

Contratos y definiciones para el sistema de orquestación de EREN.

## Responsabilidad

- Definir CognitiveEngine interface
- Definir EngineRegistry
- Definir CognitiveCycle
- Definir EngineState

## Arquitectura

```
Orchestration Contracts
    │
    ├── CognitiveEngine Protocol
    ├── EngineRegistry Type
    ├── CognitiveCycle
    ├── EngineState
    └── TransitionManager
```

## Contratos

```python
class CognitiveEngine(Protocol):
    def execute(self, context: Context) -> Result: ...
    def health_check(self) -> HealthStatus: ...
```

## Límites

- **Puede depender de:** contracts
- **Nunca depende de:** implementaciones

---
*Architecture only - no business logic*
