# EREN OS Cognitive Execution Coordinator

> **Philosophy**: The Runtime manages the system. The Router selects the Pipeline. The Pipeline executes capabilities. The Execution Coordinator coordinates the entire cognitive flow.

This document describes the Cognitive Execution Coordinator (CEC), the component responsible for coordinating the complete cognitive execution cycle from receiving an intent to session completion.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Execution Flow](#execution-flow)
4. [Coordinator Components](#coordinator-components)
5. [States](#states)
6. [Validation](#validation)
7. [Usage](#usage)
8. [Integration](#integration)
9. [Observability](#observability)
10. [Roadmap](#roadmap)

---

## Overview

The Cognitive Execution Coordinator is the orchestration engine that coordinates all components to execute a complete cognitive cycle.

### Key Principles

1. **Single Responsibility**: One component coordinates everything
2. **Runtime Agnostic**: Runtime only knows Coordinator
3. **Component Coordination**: Routes work to specialized components
4. **Observable**: Complete tracing, metrics, and events

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Runtime                                       │
│                                                                      │
│    (Only knows Coordinator)                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Cognitive Execution Coordinator                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Coordinator     │  │  Validator       │  │  Context         │  │
│  │  Engine          │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Events          │  │  Metrics         │  │  Trace           │  │
│  │                  │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Router     │    │   Pipeline   │    │    Session   │
│              │    │              │    │    Manager   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Lifecycle  │    │   Context   │    │   Scheduler  │
│   Manager    │    │   Manager    │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Module Structure

```
core/execution/
├── __init__.py           # Main exports
├── coordinator.py        # ExecutionCoordinator (main engine)
├── context.py           # ExecutionContext
├── result.py            # ExecutionResult
├── validator.py         # ExecutionValidator
├── events.py            # Event publishing
├── metrics.py           # Metrics collection
├── trace.py             # Tracing
├── types.py             # Types and enums
└── exceptions.py        # All exceptions
```

---

## Execution Flow

```
Intent
   │
   ▼
┌────────────────────────────────────┐
│     ExecutionCoordinator.execute()   │
└────────────────────────────────────┘
   │
   ├── Validate Components
   │     │
   │     ▼
   │  ┌─────────────────┐
   │  │ Validator.check() │
   │  └─────────────────┘
   │
   ├── Create Session
   │     │
   │     ▼
   │  ┌─────────────────┐
   │  │ Session Manager │
   │  └─────────────────┘
   │
   ├── Route Intent
   │     │
   │     ▼
   │  ┌─────────────────┐
   │  │ Capability      │ ──► Pipeline
   │  │ Router          │
   │  └─────────────────┘
   │
   ├── Execute Pipeline
   │     │
   │     ▼
   │  ┌─────────────────┐
   │  │ Pipeline        │ ──► Cognitive
   │  │ Executor        │     Capabilities
   │  └─────────────────┘
   │
   ├── Update Context
   │     │
   │     ▼
   │  ┌─────────────────┐
   │  │ Context Manager │
   │  └─────────────────┘
   │
   ├── Complete Session
   │     │
   │     ▼
   │  ┌─────────────────┐
   │  │ Session Manager │
   │  └─────────────────┘
   │
   ▼
ExecutionResult
```

---

## Coordinator Components

### ExecutionCoordinator

Main coordinator engine.

```python
from core.execution import ExecutionCoordinator

coordinator = ExecutionCoordinator()
```

### ExecutionContext

Context passed through execution phases.

```python
from core.execution import ExecutionContext

context = ExecutionContext(
    execution_id="exec_001",
    session_id="sess_001",
    intent_type="diagnostic",
)
```

### ExecutionValidator

Ensures all required components are available.

```python
from core.execution import ExecutionValidator

validator = ExecutionValidator()
validator.register_default_checkers()
result = validator.validate()
```

---

## States

### Execution States

| State | Description |
|-------|-------------|
| `CREATED` | Execution created |
| `INITIALIZING` | Initializing execution |
| `CREATING_SESSION` | Creating session |
| `ROUTING` | Routing intent |
| `PIPELINE_EXECUTION` | Executing pipeline |
| `UPDATING_CONTEXT` | Updating context |
| `COMPLETING_SESSION` | Completing session |
| `COMPLETED` | Execution completed |
| `FAILED` | Execution failed |
| `CANCELLED` | Execution cancelled |

### State Transitions

```
CREATED
   │
   ▼
INITIALIZING ──────────────────────────────────┐
   │                                           │
   ▼                                           │
CREATING_SESSION                               │
   │                                           │
   ▼                                           │
ROUTING                                        │
   │                                           │
   ▼                                           │
PIPELINE_EXECUTION                             │
   │                                           │
   ▼                                           │
UPDATING_CONTEXT                               │
   │                                           │
   ▼                                           │
COMPLETING_SESSION                             │
   │                                           │
   ▼                                           │
COMPLETED ◄────────────────────────────────────┘
   │
   ├── (error)
   │
   ▼
FAILED
   │
   └── (cancel)
   │
   ▼
CANCELLED
```

---

## Validation

### Component Checks

The validator checks:
- Router availability
- Pipeline availability
- Session Manager availability
- Event Bus availability

### Validation Result

```python
result = validator.validate()

print(f"Valid: {result.is_valid}")
for error in result.errors:
    print(f"Error: {error}")
```

---

## Usage

### Basic Usage

```python
from core.execution import ExecutionCoordinator

coordinator = ExecutionCoordinator()

result = coordinator.execute(
    intent_type="diagnostic",
    intent_data={"query": "chest pain"},
    session_id="session_001",
    user_id="user_001",
)

print(f"Status: {result.status}")
print(f"Pipeline: {result.selected_pipeline}")
print(f"Duration: {result.duration_ms}ms")
```

### With Router

```python
from core.execution import ExecutionCoordinator
from core.router import CapabilityRouter

router = CapabilityRouter()
coordinator = ExecutionCoordinator()

coordinator.set_router(router)

result = coordinator.execute(intent_type="diagnostic")
```

---

## Integration

### With Runtime

```python
class CognitiveRuntime:
    def __init__(self, coordinator: ExecutionCoordinator):
        self._coordinator = coordinator

    def process(self, intent):
        result = self._coordinator.execute(
            intent_type=intent.type,
            intent_data=intent.data,
        )
        return result
```

### With Router

```python
coordinator.set_router(router)
```

### With Session Manager

```python
coordinator.set_session_manager(session_manager)
```

---

## Observability

### Events

Coordinator publishes events:

| Event | Description |
|-------|-------------|
| `ExecutionStarted` | Execution started |
| `SessionCreated` | Session created |
| `RoutingStarted` | Routing started |
| `PipelineExecutionStarted` | Pipeline started |
| `ContextUpdated` | Context updated |
| `SessionCompleted` | Session completed |
| `ExecutionCompleted` | Execution completed |
| `ExecutionFailed` | Execution failed |

### Metrics

```python
from core.execution import get_execution_metrics

metrics = get_execution_metrics()
summary = metrics.get_summary()

print(f"Executions: {summary['execution_stats']['total']}")
print(f"Success Rate: {summary['execution_stats']['success_rate']}%")
```

### Tracing

```python
from core.execution import get_execution_trace

trace = get_execution_trace()
entries = trace.get_entries_by_execution("exec_001")
```

---

## Roadmap

### Phase 1: Core Infrastructure ✓
- [x] Coordinator engine
- [x] Context
- [x] Result
- [x] Validator
- [x] Events
- [x] Metrics
- [x] Tracing

### Phase 2: Advanced Features
- [ ] Parallel execution
- [ ] Execution caching
- [ ] Priority queues
- [ ] Retry policies

### Phase 3: Integration
- [ ] Runtime integration
- [ ] Boot integration
- [ ] Configuration integration

---

## References

- [Architecture Overview](./architecture-overview.md)
- [Pipeline Documentation](./pipeline.md)
- [Router Documentation](./router.md)
- [Runtime Documentation](./runtime.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
