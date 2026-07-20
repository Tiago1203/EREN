# core/context/ — Cognitive Context & Blackboard System

> **EREN NO crea copias del contexto. Todos los motores enriquecen el MISMO contexto.**

El **Cognitive Context & Blackboard System (CCBS)** es el nucleo del procesamiento
cognitivo de EREN. Todos los motores comparten UN contexto unico.

---

## Paradigma

```
ANTIGUO: Motores crean copias del contexto
==========================================

Motor A -> Copia A -> Copia B <- Motor B no ve a Motor A
                              |
                         Copia C <- Motor C no ve nada


NUEVO: UN contexto compartido
=============================

                    +------------------+
                    | CognitiveContext |
                    |   (UNICO)       |
                    +--------+---------+
                             |
     +-----------------------+-----------------------+
     |                       |                       |
     v                       v                       v
Motor A                  Motor B                Motor C
(escribe/leer)          (escribe/leer)        (escribe/leer)
```

---

## Componentes

| Archivo | Descripcion |
|---------|-------------|
| `cognitive_context.py` | CognitiveContext - contexto compartido |
| `blackboard.py` | CognitiveBlackboard - espacio compartido |
| `context_manager.py` | ContextManager - gestion de contextos |
| `context_history.py` | ContextHistory - auditoria |
| `context_snapshot.py` | ContextSnapshot - snapshots |
| `context_types.py` | Tipos: Evidence, Hypothesis, Confidence... |
| `exceptions.py` | Jerarquia de excepciones |
| `models.py` | Modelos Pydantic (legacy) |

---

## CognitiveContext

```python
@dataclass
class CognitiveContext:
    # Identity
    context_id: str
    version: int
    
    # Context
    user: UserContext
    hospital: HospitalContext
    device: DeviceContext
    incident: IncidentContext
    
    # Processing
    status: ContextStatus
    current_stage: ProcessingStage
    
    # Results
    intent: IntentResult
    evidence: tuple[Evidence, ...]
    hypotheses: tuple[Hypothesis, ...]
    diagnosis: DiagnosisResult
    response: ResponseResult
    
    # Confidence
    overall_confidence: Confidence
    
    # Blackboard
    blackboard: tuple[BlackboardEntry, ...]
```

---

## CognitiveBlackboard

Todos los motores pueden:
- **Leer** entradas de otros motores
- **Escribir** sus propias entradas
- **Nunca** modificar el trabajo de otros

```python
blackboard = CognitiveBlackboard()

# Motor A escribe evidencia
blackboard.write_evidence(
    engine_id="diagnostic_engine",
    evidence=Evidence(...),
)

# Motor B lee evidencia
evidence = blackboard.read_evidence()

# Motor B anade hipotesis
blackboard.write_hypothesis(
    engine_id="reasoning_engine",
    hypothesis=Hypothesis(...),
)
```

---

## Estados del Contexto

```
INITIALIZING -> PROCESSING -> COMPLETED
                    |
              PENDING_EVIDENCE
              PENDING_HYPOTHESIS
              PENDING_DIAGNOSIS
                    |
              FAILED / CANCELLED
```

---

## API Rapida

```python
from core.context import (
    CognitiveContext,
    CognitiveBlackboard,
    ContextManager,
    Evidence,
    Hypothesis,
)

# Crear contexto
context = CognitiveContext.create(
    correlation_id="corr-123",
    session_id="session-456",
)

# Anadir evidencia
context = context.add_evidence(
    Evidence(
        evidence_id="ev-1",
        content="Device error E101",
        confidence=Confidence(level=ConfidenceLevel.HIGH, score=0.9),
    )
)

# Anadir hipotesis
context = context.add_hypothesis(
    Hypothesis(hypothesis_id="hyp-1", description="Sensor malfunction")
)

# Completar
context = context.complete(
    response=ResponseResult(content="Diagnostico: Sensor malfunction")
)
```

---

## Context Manager

```python
manager = ContextManager()

# Crear
context = manager.create_context(correlation_id="corr-123")

# Buscar
contexts = manager.find_by_session("session-456")

# Estadisticas
stats = manager.get_statistics()
```

---

## Documentacion

- [Documentacion arquitectonica](../docs/core/cognitive-context-system.md)

## Boundaries

- **Architecture only** - no AI, no business logic
- **Immutable context** - modifications create new versions
- **Thread-safe** - designed for concurrent access
- **Pydantic models** - legacy models preserved in `models.py`
