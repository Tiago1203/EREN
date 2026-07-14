# Cognitive Workflow Engine (CWE)

## Overview

The official system for cognitive workflow execution in EREN. Allows executing long-running, persistent, and resumable processes composed of multiple decisions, agents, and capabilities.

## Philosophy

> **An agent executes tasks.**
> **A Workflow executes complete processes.**

**The Engine NEVER:**
- Knows about AI/LLM/RAG
- Knows about specific implementations
- Knows about databases

**It ONLY:**
- Creates workflows
- Persists state
- Resumes execution
- Handles checkpoints
- Manages rollback
- Provides observability
- Handles fault recovery

## Architecture

```
Execution Coordinator
        │
        ▼
Decision Engine
        │
        ▼
Workflow Engine
        │
        ├── Workflow Planner
        ├── Workflow Runtime
        ├── State Manager
        ├── Checkpoint Manager
        ├── Execution Graph
        └── Agent Platform
```

## Supported Workflow Types

- **Linear Workflows**: Sequential execution
- **Conditional Workflows**: Branch based on conditions
- **Parallel Workflows**: Concurrent execution
- **Loop Workflows**: Iterative execution
- **Subworkflows**: Nested workflows
- **Saga Workflows**: Compensation-based workflows

## Features

- ✅ Linear workflows
- ✅ Conditional workflows
- ✅ Parallel workflows
- ✅ Loops
- ✅ Subworkflows
- ✅ Human approval
- ✅ Timeouts
- ✅ Retries
- ✅ Compensation
- ✅ Saga Pattern
- ✅ Checkpoint Recovery

## Components

| Component | Description |
|-----------|-------------|
| `engine.py` | Main workflow engine |
| `runtime.py` | Workflow runtime |
| `planner.py` | Workflow planner |
| `graph.py` | Execution graph |
| `state.py` | State management |
| `checkpoint.py` | Checkpoint management |
| `executor.py` | Task executor |
| `scheduler.py` | Task scheduler |
| `events.py` | Event publishing |
| `metrics.py` | Metrics collection |
| `types.py` | Type definitions |

## Usage

### Creating a Workflow

```python
from core.workflows import (
    get_workflow_engine,
    WorkflowType,
    NodeType,
)

engine = get_workflow_engine()

# Create workflow definition
workflow = engine.create_definition(
    name="Patient Admission",
    description="Patient admission workflow",
    workflow_type=WorkflowType.LINEAR,
)

# Add nodes
node1 = engine.add_node(
    workflow_id=workflow.workflow_id,
    name="Validate Patient",
    node_type=NodeType.TASK,
    config={"validator": "patient_validator"},
)

node2 = engine.add_node(
    workflow_id=workflow.workflow_id,
    name="Create Record",
    node_type=NodeType.TASK,
    config={"action": "create_record"},
    depends_on=[node1.node_id],
)

# Add edges
engine.add_edge(workflow.workflow_id, node1.node_id, node2.node_id)
```

### Executing a Workflow

```python
# Start execution
execution = engine.start(
    workflow_id=workflow.workflow_id,
    input_data={"patient_id": "P123"},
)

print(f"Status: {execution.status}")
print(f"Progress: {execution.progress_percent()}%")
```

### Pausing and Resuming

```python
# Pause
engine.pause(execution.execution_id)

# Resume
execution = engine.resume(execution.execution_id)
```

### Checkpoint and Recovery

```python
# Create checkpoint
engine.create_checkpoint(
    execution_id=execution.execution_id,
    metadata={"reason": "periodic_save"},
)

# Restore from checkpoint
restored = engine.restore(checkpoint_id="...")
```

## Integration

```
Decision Engine
        │
        ▼
Workflow Engine
        │
        ▼
Agent Platform
        │
        ▼
Capability SDK
        │
        ▼
Memory
        │
        ▼
Retrieval
        │
        ▼
Provider Layer
```

---

*An agent executes tasks. A Workflow executes complete processes.*
