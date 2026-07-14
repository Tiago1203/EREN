# EREN OS Cognitive Capability Pipeline

> **Philosophy**: The Runtime does not decide which motors to execute. The Pipeline decides which cognitive capabilities participate in a cycle.

This document describes the Cognitive Capability Pipeline (CCP), the component responsible for dynamically executing cognitive capabilities of EREN OS.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Pipeline Components](#pipeline-components)
4. [Stage Types](#stage-types)
5. [Execution Flow](#execution-flow)
6. [States](#states)
7. [Policies](#policies)
8. [Usage](#usage)
9. [Integration](#integration)
10. [Observability](#observability)
11. [Roadmap](#roadmap)

---

## Overview

The Cognitive Capability Pipeline is the execution engine that orchestrates cognitive capabilities. It separates the Runtime from specific motor implementations, allowing:

- **Dynamic execution**: Pipelines can be composed based on intent
- **Policy-based execution**: Different policies control failure handling
- **Observable execution**: Full tracing, metrics, and event publishing
- **Extensible stages**: New capabilities can be added without modifying Runtime

### Key Principles

1. **Runtime Agnostic**: Runtime only knows Pipeline, not specific motors
2. **Contract-Based**: All stages communicate via contracts
3. **Policy-Driven**: Execution behavior controlled by policies
4. **Observable**: Complete tracing, metrics, and events

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Runtime                                       │
│                                                                      │
│    (Only knows Pipeline, not specific motors)                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Cognitive Pipeline                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Pipeline        │  │  Executor        │  │  Policy          │  │
│  │  Builder         │  │                  │  │  Engine          │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Registry        │  │  Validator       │  │  Context         │  │
│  │                  │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Pipeline Stages                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PlanningStage │ KnowledgeStage │ MemoryStage │ ReasoningStage        │
│                                                                      │
│  DecisionStage │ ToolStage │ ContextUpdateStage │ CustomStage         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Structure

```
core/pipeline/
├── __init__.py           # Main exports
├── pipeline.py            # CognitivePipeline (main engine)
├── context.py            # PipelineContext (shared data)
├── stage.py              # PipelineStage (base class)
├── executor.py           # PipelineExecutor
├── builder.py            # PipelineBuilder
├── registry.py           # PipelineRegistry
├── policy.py             # Execution policies
├── validator.py          # PipelineValidator
├── events.py             # Event publishing
├── metrics.py           # Metrics collection
├── trace.py             # Tracing
├── types.py             # Types and enums
└── exceptions.py         # All exceptions
```

---

## Pipeline Components

### CognitivePipeline

Main pipeline engine that orchestrates stage execution.

```python
from core.pipeline import CognitivePipeline

pipeline = CognitivePipeline(
    name="my_pipeline",
    stages=[PlanningStage(), ReasoningStage(), DecisionStage()],
    policy=StopOnFailurePolicy(),
)
```

### PipelineContext

Shared context that flows through all stages.

```python
context = PipelineContext(
    pipeline_id="pipeline_001",
    correlation_id="corr_123",
    intent_type="diagnostic",
    intent_data={"query": "..."},
)
```

### PipelineStage

Abstract base class for all stages.

```python
class MyStage(PipelineStage):
    def describe(self) -> str:
        return "My custom stage"

    async def execute(self, context: PipelineContext) -> Any:
        # Process context
        return {"result": "processed"}
```

---

## Stage Types

### Built-in Stages

| Stage | Type | Required | Description |
|-------|------|----------|-------------|
| `PlanningStage` | PLANNING | Yes | Decomposes intent into plan |
| `KnowledgeStage` | KNOWLEDGE | Yes | Retrieves relevant knowledge |
| `MemoryStage` | MEMORY | Yes | Memory operations |
| `ReasoningStage` | REASONING | Yes | Logical reasoning |
| `DecisionStage` | DECISION | Yes | Decision making |
| `ToolStage` | TOOL | No | Tool execution |
| `ContextUpdateStage` | CONTEXT_UPDATE | Yes | Updates shared context |

### Custom Stages

```python
from core.pipeline import PipelineStage, StageType

class CustomStage(PipelineStage):
    def __init__(self):
        super().__init__(
            name="custom_stage",
            stage_type=StageType.CUSTOM,
            required=True,
        )

    def describe(self) -> str:
        return "My custom processing"

    async def execute(self, context: PipelineContext) -> Any:
        # Custom logic
        return {"custom": "result"}
```

---

## Execution Flow

### Pipeline Execution

```
Intent
   │
   ▼
Pipeline.execute()
   │
   ├── Validate
   │
   ▼
Stage 1: Planning
   │
   ▼
Stage 2: Knowledge
   │
   ▼
Stage 3: Memory
   │
   ▼
Stage 4: Reasoning
   │
   ▼
Stage 5: Decision
   │
   ▼
Stage 6: Tool (optional)
   │
   ▼
Stage 7: Context Update
   │
   ▼
PipelineResult
```

### Context Flow

```python
# Context flows through all stages
context = PipelineContext(...)

# Each stage can:
context.set("key", value)      # Set shared data
context.get("key")               # Get shared data
context.get_stage_result("name")  # Get previous stage result
context.add_stage_result(result)   # Add current stage result
```

---

## States

### Pipeline States

| State | Description | Can Transition To |
|-------|-------------|-------------------|
| `CREATED` | Pipeline created | READY |
| `READY` | Pipeline validated | RUNNING, CANCELLED |
| `RUNNING` | Pipeline executing | WAITING, PAUSED, COMPLETED, FAILED, CANCELLED |
| `WAITING` | Pipeline waiting | RUNNING, CANCELLED |
| `PAUSED` | Pipeline paused | RUNNING, CANCELLED |
| `COMPLETED` | Pipeline completed successfully | - |
| `FAILED` | Pipeline failed | CREATED |
| `CANCELLED` | Pipeline cancelled | CREATED |

### Stage States

| State | Description |
|-------|-------------|
| `PENDING` | Stage not yet executed |
| `READY` | Stage ready to execute |
| `RUNNING` | Stage executing |
| `SKIPPED` | Stage skipped (optional failed) |
| `FAILED` | Stage failed |
| `COMPLETED` | Stage completed |
| `CANCELLED` | Stage cancelled |

---

## Policies

### Available Policies

| Policy | Behavior |
|--------|----------|
| `StopOnFailure` | Stop pipeline on required stage failure |
| `ContinueOnFailure` | Continue pipeline even on failure |
| `StrictExecution` | Fail on any issue |
| `SkipOptional` | Skip optional stages on failure |
| `RetryStage` | Retry failed stages |

### Usage

```python
from core.pipeline import StopOnFailurePolicy, RetryStagePolicy

# Stop on failure (default)
pipeline = CognitivePipeline(..., policy=StopOnFailurePolicy())

# Retry stages
pipeline = CognitivePipeline(
    ...,
    policy=RetryStagePolicy(max_retries=3)
)
```

---

## Usage

### Basic Usage

```python
from core.pipeline import PipelineBuilder, PlanningStage, ReasoningStage

# Build pipeline
pipeline = (
    PipelineBuilder()
    .named("my_pipeline")
    .with_stage(PlanningStage)
    .with_stage(ReasoningStage)
    .build()
)

# Execute
result = pipeline.execute(
    intent={"query": "diagnose equipment"},
    session_id="session_001",
)

print(f"Status: {result.status}")
print(f"Duration: {result.duration_ms}ms")
```

### Using Presets

```python
from core.pipeline import PipelinePreset

# Create from preset
pipeline = PipelinePreset.build_preset("default")
result = pipeline.execute(intent={"query": "..."})
```

### Registry Usage

```python
from core.pipeline import get_pipeline, register_pipeline

# Register pipeline
register_pipeline("my_pipeline", pipeline)

# Get from registry
pipeline = get_pipeline("my_pipeline")
```

---

## Integration

### With Runtime

The Runtime only knows the Pipeline interface:

```python
class CognitiveRuntime:
    def __init__(self, pipeline: CognitivePipeline):
        self._pipeline = pipeline

    def execute(self, intent):
        return self._pipeline.execute(intent)
```

### With DI Container

```python
from core.container import CognitiveContainer

container = CognitiveContainer()
container.register("Pipeline", CognitivePipeline, ...)

pipeline = container.resolve("Pipeline")
```

### With Event Bus

```python
from core.pipeline import PipelineEventPublisher
from core.events import get_global_bus

event_bus = get_global_bus()
publisher = PipelineEventPublisher(event_bus)

pipeline.set_event_publisher(publisher)
```

---

## Observability

### Events

Pipeline publishes events for each operation:

| Event | Description |
|-------|-------------|
| `PipelineCreated` | Pipeline created |
| `PipelineStarted` | Pipeline execution started |
| `PipelineCompleted` | Pipeline completed |
| `PipelineFailed` | Pipeline failed |
| `StageStarted` | Stage execution started |
| `StageCompleted` | Stage completed |

### Metrics

```python
from core.pipeline import get_pipeline_metrics

metrics = get_pipeline_metrics()
summary = metrics.get_summary()

print(f"Pipelines: {summary['pipeline_stats']['executed']}")
print(f"Success Rate: {summary['pipeline_stats']['success_rate']}%")
```

### Tracing

```python
from core.pipeline import get_pipeline_trace

trace = get_pipeline_trace()
entries = trace.get_entries_by_pipeline("pipeline_001")
```

---

## Roadmap

### Phase 1: Core Infrastructure ✓
- [x] Pipeline engine
- [x] Stage base class
- [x] Executor
- [x] Policies
- [x] Registry
- [x] Validator

### Phase 2: Observability ✓
- [x] Event publishing
- [x] Metrics collection
- [x] Tracing

### Phase 3: Advanced Features
- [ ] Parallel stage execution
- [ ] Conditional stage execution
- [ ] Stage caching
- [ ] Pipeline versioning

### Phase 4: Integration
- [ ] Runtime integration
- [ ] Orchestrator integration
- [ ] Boot integration
- [ ] Configuration integration

---

## References

- [Architecture Overview](./architecture-overview.md)
- [Runtime Documentation](./runtime.md)
- [Event System](./events.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
