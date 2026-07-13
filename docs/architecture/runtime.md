# Cognitive Runtime — EREN Cognitive Operating System

> **PR-020: Cognitive Runtime & First End-to-End Cognitive Cycle**

## Overview

The Cognitive Runtime is the core coordinator of EREN's Cognitive Operating System. It orchestrates the complete cognitive cycle through all existing components, using only contracts and events—no AI, no implementations.

## Philosophy

The Runtime **DOES NOT**:
- Think (that's the Reasoning Engine)
- Decide (that's the Decision Engine)
- Use AI or LLMs
- Implement business logic
- Store or retrieve actual data

The Runtime **ONLY**:
- Coordinates the flow through existing contracts
- Manages the lifecycle of sessions and cycles
- Publishes events for observability
- Collects metrics and traces
- Validates component availability

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     COGNITIVE RUNTIME                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Builder    │  │  Validator  │  │  Health Checker      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                    STATE MACHINE                         │    │
│  │  CREATED → INITIALIZING → INITIALIZED → BOOTING →       │    │
│  │  BOOTED → VALIDATING → VALIDATED → RUNNING → SHUTTING   │    │
│  └──────────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                    EXECUTOR                             │    │
│  │  Planning → Knowledge → Memory → Reasoning → Decision →  │    │
│  │  Action → Context Update                                │    │
│  └──────────────────────────────────────────────────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Metrics    │  │    Trace    │  │   Event Publisher    │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INTEGRATED COMPONENTS                           │
├─────────────────────────────────────────────────────────────────┤
│  Composition Root    │  DI Container      │  Event Bus            │
│  Capability Registry │  Boot Manager     │  Session Manager      │
│  Lifecycle Manager   │  Orchestrator     │  Scheduler            │
│  Planner Engine     │  Knowledge Engine │  Memory Engine         │
│  Reasoning Engine   │  Decision Engine   │  Tool Engine          │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
core/runtime/
├── __init__.py              # Module exports
├── runtime.py               # Main CognitiveRuntime class
├── runtime_builder.py       # Fluent builder API
├── runtime_configuration.py # Configuration dataclasses
├── runtime_context.py       # Execution context
├── runtime_executor.py      # Cognitive cycle executor
├── runtime_state.py         # State management
├── runtime_events.py        # Event definitions
├── runtime_metrics.py       # Metrics collection
├── runtime_trace.py        # Tracing
├── runtime_health.py       # Health checks
├── runtime_validator.py     # Validation
└── exceptions.py            # All exceptions
```

## State Machine

The Runtime follows a strict state machine:

```
┌─────────┐
│ CREATED │ ────► INITIALIZING ────► INITIALIZED
└─────────┘              │                    │
                        ▼                    ▼
               ┌────────────────┐   ┌───────────┐
               │ INITIALIZATION_ │   │  BOOTING  │
               │    FAILED       │   └─────┬─────┘
               └────────────────┘         │
                                          ▼
                                 ┌──────────────┐
                                 │ BOOT_FAILED  │
                                 └──────────────┘
                                          │
                                          ▼
                                   ┌───────────┐
                                   │  BOOTED   │
                                   └─────┬─────┘
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │ VALIDATING    │
                                 └───────┬───────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
           ┌────────────────┐    ┌──────────────┐    ┌──────────┐
           │ VALIDATION_    │    │  VALIDATED   │    │ RUNNING  │
           │ FAILED         │    └──────┬───────┘    └────┬─────┘
           └────────────────┘           │                  │
                                       ▼                  ▼
                              ┌──────────────┐    ┌──────────────┐
                              │ VALIDATION_  │    │ SHUTTING_    │
                              │ FAILED       │    │ DOWN         │
                              └──────────────┘    └──────┬──────┘
                                                         │
                                                         ▼
                                                  ┌───────────┐
                                                  │  STOPPED  │
                                                  └───────────┘
```

## First Cognitive Cycle

The first cognitive cycle traverses all components:

```
User Intent
    │
    ▼
Runtime.start()
    │
    ▼
┌─────────────────┐
│ Boot Manager    │ ◄── Composition Root
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DI Container    │ ◄── All contracts registered
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Session Manager │ ◄── New cognitive session created
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Lifecycle       │
│ Manager         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Orchestrator    │ ◄── Session state machine
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Planner Engine  │ ◄── Create execution plan
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Knowledge       │ ◄── Retrieve relevant knowledge
│ Engine          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Memory Engine   │ ◄── Retrieve relevant memories
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Reasoning       │ ◄── Generate hypotheses
│ Engine          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Decision        │ ◄── Make decisions
│ Engine          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Tool Engine     │ ◄── Request actions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cognitive       │ ◄── Update context
│ Context         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Session Closed  │
└────────┬────────┘
         │
         ▼
Runtime Complete
```

## Events Published

The Runtime publishes these events during its lifecycle:

### Lifecycle Events
- `RuntimeStarted` - Runtime initialization begun
- `RuntimeInitialized` - All components initialized
- `RuntimeBootStarted` - Boot process begun
- `RuntimeBootCompleted` - Boot process completed
- `RuntimeValidationStarted` - Validation begun
- `RuntimeValidationCompleted` - Validation completed

### Session Events
- `SessionCreated` - New session created
- `SessionStarted` - Session started
- `SessionCompleted` - Session completed successfully
- `SessionFailed` - Session failed

### Cognitive Cycle Events
- `CognitiveCycleStarted` - Cycle begun
- `CognitiveCycleCompleted` - Cycle completed
- `CognitiveCycleFailed` - Cycle failed

### Stage Events
- `PlanningStarted` / `PlanningCompleted` / `PlanningFailed`
- `KnowledgeRequested` / `KnowledgeRetrieved` / `KnowledgeFailed`
- `MemoryRequested` / `MemoryRetrieved` / `MemoryFailed`
- `ReasoningStarted` / `ReasoningCompleted` / `ReasoningFailed`
- `DecisionCreated` / `DecisionApplied` / `DecisionFailed`
- `ActionGenerated` / `ActionExecuted` / `ActionFailed`
- `ContextUpdated` / `ContextSnapshot`

### Completion Events
- `RuntimeCompleted` - Runtime shutdown completed
- `RuntimeFailed` - Runtime encountered critical error
- `RuntimeShutdown` - Runtime shutdown initiated

## Usage

### Simple Usage

```python
from core.runtime import CognitiveRuntime

runtime = CognitiveRuntime()
runtime.initialize().boot().validate().start()

session = runtime.create_session()
runtime.execute_cognitive_cycle(
    session,
    intent={"query": "Diagnose device issue"}
)

print(f"Events published: {len(runtime.events)}")
print(f"Metrics: {runtime.metrics.get_summary()}")

runtime.shutdown()
```

### Builder Usage

```python
from core.runtime import RuntimeBuilder

runtime = (
    RuntimeBuilder()
    .with_name("My Runtime")
    .with_version("1.0.0")
    .with_simulation_mode(True)
    .with_simulation_delay(100)
    .with_auto_boot(True)
    .with_auto_validate(True)
    .build()
)

runtime.start()

session = runtime.create_session()
runtime.execute_cognitive_cycle(session, intent={"query": "test"})

runtime.shutdown()
```

### Presets

```python
from core.runtime import (
    create_development_runtime,
    create_production_runtime,
    create_testing_runtime,
)

# Development
runtime = create_development_runtime()

# Production
runtime = create_production_runtime()

# Testing
runtime = create_testing_runtime()
```

## Configuration

Key configuration options:

| Option | Default | Description |
|--------|---------|-------------|
| `runtime_name` | "EREN Cognitive Runtime" | Runtime name |
| `runtime_version` | "1.0.0" | Runtime version |
| `environment` | "development" | Environment |
| `simulation_mode` | `True` | Use simulated data |
| `simulation_delay_ms` | `100` | Delay between stages |
| `auto_boot` | `True` | Auto-boot on start |
| `auto_validate` | `True` | Auto-validate |
| `validate_before_start` | `True` | Validate before start |
| `strict_validation` | `False` | Treat warnings as errors |
| `enable_metrics` | `True` | Collect metrics |
| `record_trace` | `True` | Record traces |

## Metrics

The Runtime collects these metrics:

- **Initialization**: Duration of initialization
- **Boot**: Duration of boot process
- **Validation**: Duration of validation
- **Sessions**: Created, completed, failed counts
- **Cycles**: Completed, failed, average duration
- **Engines**: Execution count, success/failure, durations
- **Events**: Published count, failed count
- **Errors**: Total and critical errors

## Health Checks

The Runtime validates:

- [ ] DI Container ready
- [ ] Event Bus active
- [ ] Capability Registry active
- [ ] Boot Manager completed
- [ ] Session Manager available
- [ ] Lifecycle Manager available
- [ ] Orchestrator available
- [ ] Scheduler available
- [ ] Planner Engine available (or degraded)
- [ ] Knowledge Engine available (or degraded)
- [ ] Memory Engine available (or degraded)
- [ ] Reasoning Engine available (or degraded)
- [ ] Decision Engine available (or degraded)
- [ ] Tool Engine available (or degraded)

## Validation

Before starting, the Runtime validates:

1. Configuration is valid
2. Composition Root is built
3. Container is not disposed
4. Event Bus has required methods
5. Capability Registry is available
6. Boot Manager is ready
7. All engines are available (or in simulation mode)

## Tracing

The Runtime traces:

- All state transitions
- All engine executions with timing
- All event publications
- All errors and failures
- Correlation IDs for tracking

## Roadmap

### Phase 1 (Current) ✓
- [x] Basic runtime structure
- [x] State machine
- [x] Event publishing
- [x] Metrics collection
- [x] Trace recording
- [x] Health checks
- [x] Validation
- [x] First cognitive cycle (simulation)

### Phase 2
- [ ] Real engine integration
- [ ] Async execution
- [ ] Parallel session handling
- [ ] Error recovery

### Phase 3
- [ ] Distributed runtime support
- [ ] Cluster coordination
- [ ] High availability

## Best Practices

1. **Always shutdown properly**: Use context manager or call `shutdown()`
2. **Check health before starting**: Use `health_check()` method
3. **Validate in strict mode for production**: Ensures all components are ready
4. **Monitor metrics**: Track cycle duration and error rates
5. **Use correlation IDs**: Track requests across components

## Troubleshooting

### Runtime won't start
1. Check health: `runtime.health_check()`
2. Check validation: `runtime.validate()`
3. Check state: `runtime.state`
4. Review events: `runtime.events`

### Session fails
1. Check session errors: `session.errors`
2. Check trace: `runtime.trace.get_engine_executions()`
3. Review metrics: `runtime.metrics.get_summary()`

### Slow cycles
1. Check metrics: `runtime.metrics.engine_metrics`
2. Identify slow engines
3. Consider increasing timeout

## License

Part of EREN Cognitive Operating System.
See LICENSE for details.
