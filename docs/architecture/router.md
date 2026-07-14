# EREN OS Cognitive Capability Router

> **Philosophy**: The Runtime does not select pipelines. The Pipeline does not decide when to execute. The Capability Router decides which Cognitive Pipeline to use.

This document describes the Cognitive Capability Router (CCR), the component responsible for dynamically selecting which Cognitive Pipeline should execute based on context, intent, available capabilities, and system policies.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Router Components](#router-components)
4. [Routing Flow](#routing-flow)
5. [Policies](#policies)
6. [Matching](#matching)
7. [Usage](#usage)
8. [Integration](#integration)
9. [Observability](#observability)
10. [Roadmap](#roadmap)

---

## Overview

The Cognitive Capability Router is the decision engine that selects the appropriate pipeline for each intent. It separates intent interpretation from pipeline execution.

### Key Principles

1. **Runtime Agnostic**: Runtime only knows Router, not specific pipelines
2. **Policy-Based Selection**: Different policies control selection strategy
3. **Rule-Driven**: Rules determine pipeline eligibility
4. **Observable**: Complete tracing, metrics, and events

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Runtime                                       │
│                                                                      │
│    (Only knows Router, not specific pipelines)                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Capability Router                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Router          │  │  Matcher        │  │  Selector         │  │
│  │  Engine          │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Registry        │  │  Policies        │  │  Context         │  │
│  │                  │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Pipeline Registry                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  MedicalPipeline │ MaintenancePipeline │ ResearchPipeline │ ...    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Structure

```
core/router/
├── __init__.py           # Main exports
├── router.py             # CapabilityRouter (main engine)
├── context.py           # RouterContext (routing context)
├── result.py            # RoutingResult
├── matcher.py           # PipelineMatcher
├── selector.py          # PipelineSelector
├── registry.py          # RoutingRegistry
├── policy.py            # Routing policies
├── events.py            # Event publishing
├── metrics.py           # Metrics collection
├── trace.py             # Tracing
├── types.py             # Types and enums
└── exceptions.py        # All exceptions
```

---

## Router Components

### CapabilityRouter

Main router engine that orchestrates pipeline selection.

```python
from core.router import CapabilityRouter

router = CapabilityRouter(
    default_policy=RoutingPolicy.HIGHEST_SCORE,
    fallback_enabled=True,
)
```

### RouterContext

Context passed through routing operations.

```python
context = RouterContext(
    intent_type="diagnostic",
    session_id="session_001",
    available_capabilities=["knowledge", "memory", "reasoning"],
)
```

### PipelineMetadata

Metadata for a routable pipeline.

```python
metadata = PipelineMetadata(
    pipeline_name="MedicalPipeline",
    pipeline_id="medical_pipeline",
    tags=("medical", "diagnosis"),
    priority=100,
    required_capabilities=("knowledge", "reasoning"),
    intent_types=("diagnostic", "treatment"),
)
```

---

## Routing Flow

```
Intent
   │
   ▼
Router.route()
   │
   ├── Create Context
   │
   ▼
Matcher.match()
   │
   ├── Match Intent Type
   ├── Match Tags
   ├── Check Capabilities
   ├── Evaluate Priority
   │
   ▼
Selector.select()
   │
   ├── Apply Policy
   ├── Select Pipeline
   │
   ▼
RoutingResult
```

---

## Policies

### Available Policies

| Policy | Behavior |
|--------|----------|
| `FirstMatch` | Select first matching pipeline |
| `HighestScore` | Select highest scoring pipeline |
| `Priority` | Select highest priority pipeline |
| `Strict` | Require exact match |
| `Weighted` | Combine score and priority |
| `Fallback` | Try policies in order |

### Usage

```python
from core.router import CapabilityRouter, RoutingPolicy

router = CapabilityRouter(
    default_policy=RoutingPolicy.HIGHEST_SCORE,
)
```

---

## Matching

### Match Results

| Result | Score Range | Description |
|--------|-------------|-------------|
| `EXACT` | 90-100 | Perfect match |
| `PARTIAL` | 50-89 | Partial match |
| `POTENTIAL` | 1-49 | Potential match |
| `NO_MATCH` | 0 | No match |

### Matching Factors

- Intent type matching
- Tag matching
- Capability requirements
- Priority
- Custom conditions

---

## Usage

### Basic Usage

```python
from core.router import CapabilityRouter

router = CapabilityRouter()

result = router.route(
    intent_type="diagnostic",
    session_id="session_001",
    available_capabilities=["knowledge", "memory", "reasoning"],
)

print(f"Selected: {result.selected_pipeline.pipeline_name}")
print(f"Policy: {result.policy_used.value}")
print(f"Duration: {result.duration_ms}ms")
```

### Using Registry

```python
from core.router import get_routing_registry

registry = get_routing_registry()
pipelines = registry.list_pipelines()
```

### Custom Policy

```python
from core.router import CapabilityRouter, WeightedPolicy

router = CapabilityRouter(
    policy=WeightedPolicy(score_weight=0.7, priority_weight=0.3),
)
```

---

## Integration

### With Runtime

```python
class CognitiveRuntime:
    def __init__(self, router: CapabilityRouter):
        self._router = router

    def execute(self, intent):
        result = self._router.route(
            intent_type=intent.type,
            intent_data=intent.data,
        )
        return result.selected_pipeline.execute(intent)
```

### With Pipeline Registry

```python
from core.router import get_routing_registry
from core.router.types import PipelineMetadata

registry = get_routing_registry()
registry.register_pipeline(PipelineMetadata(...))
```

### With DI Container

```python
from core.container import CognitiveContainer

container = CognitiveContainer()
container.register("Router", CapabilityRouter, ...)
```

---

## Observability

### Events

Router publishes events for each operation:

| Event | Description |
|-------|-------------|
| `RoutingStarted` | Routing operation started |
| `RoutingCompleted` | Routing completed |
| `RoutingFailed` | Routing failed |
| `PipelineMatched` | Pipeline matched intent |
| `PipelineSelected` | Pipeline selected |

### Metrics

```python
from core.router import get_router_metrics

metrics = get_router_metrics()
summary = metrics.get_summary()

print(f"Routings: {summary['routing_stats']['executed']}")
print(f"Success Rate: {summary['routing_stats']['success_rate']}%")
```

### Tracing

```python
from core.router import get_router_trace

trace = get_router_trace()
entries = trace.get_entries_by_intent("diagnostic")
```

---

## Default Pipelines

The router registers default pipelines:

| Pipeline | Priority | Intent Types |
|----------|----------|--------------|
| `MedicalPipeline` | 100 | diagnostic, treatment, prescription |
| `MaintenancePipeline` | 50 | maintenance, repair, inspection |
| `ResearchPipeline` | 30 | research, analysis, query |
| `EmergencyPipeline` | 200 | emergency, critical, alert |

---

## Roadmap

### Phase 1: Core Infrastructure ✓
- [x] Router engine
- [x] Matcher
- [x] Selector
- [x] Policies
- [x] Registry
- [x] Events
- [x] Metrics
- [x] Tracing

### Phase 2: Advanced Features
- [ ] ML-based selection
- [ ] A/B testing
- [ ] Pipeline versioning
- [ ] Dynamic rules

### Phase 3: Integration
- [ ] Runtime integration
- [ ] Orchestrator integration
- [ ] Boot integration
- [ ] Configuration integration

---

## References

- [Architecture Overview](./architecture-overview.md)
- [Pipeline Documentation](./pipeline.md)
- [Runtime Documentation](./runtime.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
