# Cognitive Agent Runtime (CAR)

## Overview

The official runtime for cognitive agents in EREN. Allows multiple specialized agents to collaborate.

## Philosophy

> **Decision Engine decides.**
> **Agents execute.**
> **Runtime coordinates.**

**The Runtime NEVER:**
- Knows about OpenAI
- Knows about models
- Knows about retrieval
- Knows about databases

**It ONLY:**
- Registers agents
- Schedules tasks
- Coordinates communication
- Manages lifecycle
- Tracks health
- Collects metrics

## Architecture

```
Execution Coordinator
        │
        ▼
Decision Engine
        │
        ▼
Cognitive Agent Runtime
        │
        ├── Agent Registry
        ├── Agent Scheduler
        ├── Agent Communicator
        ├── Lifecycle Manager
        ├── Health Manager
        ├── Context Manager
        ├── Capability Registry
        ├── Event Bus
        └── Metrics Collector
```

## Specialized Agents

- **Engineering Agent**: Technical analysis and diagnostics
- **Medical Agent**: Medical diagnosis and treatment
- **Research Agent**: Research and knowledge synthesis
- **Device Agent**: Device management and configuration
- **Knowledge Agent**: Knowledge retrieval and search
- **Memory Agent**: Memory operations
- **Vision Agent**: Visual analysis
- **Speech Agent**: Speech processing
- **Custom Agents**: User-defined specializations

## Components

| Component | Responsibility |
|-----------|----------------|
| `runtime.py` | Main runtime orchestrator |
| `registry.py` | Agent registration and discovery |
| `scheduler.py` | Task scheduling and execution |
| `communicator.py` | Inter-agent communication |
| `lifecycle.py` | Lifecycle management |
| `health.py` | Health monitoring |
| `context.py` | Shared context |
| `capabilities.py` | Capability registry |
| `events.py` | Event publishing |
| `metrics.py` | Performance metrics |
| `types.py` | Type definitions |

## Usage

```python
from core.agents import (
    CognitiveAgentRuntime,
    AgentManifest,
    AgentCapability,
    AgentType,
    get_agent_runtime,
)

# Get runtime
runtime = get_agent_runtime()

# Start runtime
runtime.start()

# Register an agent
manifest = AgentManifest(
    agent_id="medical-agent-1",
    name="Medical Agent",
    agent_type=AgentType.MEDICAL,
    description="Medical diagnosis agent",
    capabilities=[
        AgentCapability(
            name="medical.diagnose",
            description="Provide diagnosis",
        ),
    ],
)
runtime.register_agent(manifest)

# Submit a task
task = runtime.submit_task(
    capability="medical.diagnose",
    description="Diagnose patient symptoms",
    input_data={"symptoms": ["fever", "cough"]},
    priority=5,
)

# Execute task
runtime.start_task(task.task_id, "medical-agent-1")

# Complete task
result = runtime.complete_task(task.task_id, {"diagnosis": "flu"})

print(f"Progress: {result}")
```

## Agent Registration

```python
from core.agents import AgentManifest, AgentCapability, AgentType

manifest = AgentManifest(
    agent_id="engineering-agent-1",
    name="Engineering Agent",
    agent_type=AgentType.ENGINEERING,
    description="Engineering diagnostics agent",
    capabilities=[
        AgentCapability(
            name="engineering.diagnose",
            description="Diagnose technical issues",
            risk_level="medium",
        ),
        AgentCapability(
            name="engineering.analyze",
            description="Analyze technical data",
        ),
    ],
    max_concurrent_tasks=2,
    timeout_seconds=120.0,
)
```

## Task Scheduling

```python
# Submit task with dependencies
task1 = runtime.submit_task(
    capability="device.status",
    description="Check device status",
)

task2 = runtime.submit_task(
    capability="device.diagnostics",
    description="Run diagnostics",
    depends_on=[task1.task_id],
)

# Get ready tasks
ready = runtime.get_ready_tasks()
```

## Inter-Agent Communication

```python
# Send message
runtime.send_message(
    sender_id="medical-agent-1",
    receiver_id="knowledge-agent-1",
    content={"query": "symptoms of flu"},
)

# Receive message (in agent)
communicator = get_communicator()
message = communicator.receive("medical-agent-1")
```

## Health Monitoring

```python
from core.agents import get_health_manager

health = get_health_manager()

# Get agent health
agent_health = health.get_health("medical-agent-1")
print(f"Status: {agent_health.status}")
print(f"Uptime: {agent_health.uptime_seconds}s")

# Check stale agents
stale = health.check_stale_agents(timeout_seconds=60.0)
```

## Events

```python
from core.agents import get_event_bus, AgentEventType

events = get_event_bus()

# Subscribe to events
def on_task_completed(event):
    print(f"Task {event.task_id} completed!")

events.subscribe(AgentEventType.TASK_COMPLETED, on_task_completed)

# Get history
history = events.get_history(limit=100)
```

## Metrics

```python
from core.agents import get_metrics_collector

metrics = get_metrics_collector()

# Get report
report = metrics.generate_report()
print(report)

# Get agent metrics
agent_metrics = metrics.get_agent_metrics("medical-agent-1")
```

## Capabilities

```python
from core.agents import get_capability_registry

registry = get_capability_registry()

# Get capability
cap = registry.get_capability("medical.diagnose")

# Find agents with capability
agents = registry.find_agents_with_capability("medical.diagnose")
```

---

*Decision Engine decides. Agents execute. Runtime coordinates.*
