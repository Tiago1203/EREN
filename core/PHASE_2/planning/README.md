# Cognitive Planning Engine (CPE)

## Overview

The first cognitive planning system of EREN. Transforms user intent into execution plans.

## Philosophy

> LLM responds.
> Planning Engine decides what to do.

**The Planning Engine NEVER:**
- Executes tasks
- Queries providers
- Uses OpenAI directly
- Consults memory
- Consults retrieval

**It ONLY:**
- Analyzes goals
- Decomposes into tasks
- Resolves dependencies
- Builds execution plans

## Architecture

```
Execution Coordinator
        │
        ▼
Cognitive Planning Engine
        │
        ├──► Goal Analyzer
        │        │
        │        └──► Intent Analysis
        │        └──► Goal Type Detection
        │
        ├──► Task Decomposer
        │        │
        │        └──► Goal → Tasks
        │        └──► Priority Assignment
        │
        ├──► Dependency Resolver
        │        │
        │        └──► Execution Order
        │        └──► Parallel Groups
        │
        └──► Plan Builder
                 │
                 └──► Execution Plan
                 └──► Estimates

        ▼
Execution Plan (Tasks)
```

## Example

**User Input:**
```
"The Philips MX450 monitor won't turn on. Analyze the problem."
```

**Planning Engine Output:**

```
Plan: troubleshooting_philips_mx450
Tasks:
  1. Check device status        [READY]      Priority: HIGH
  2. Retrieve device history    [BLOCKED:1]  Priority: HIGH
  3. Find technical docs        [BLOCKED:1]  Priority: HIGH
  4. Search maintenance prots   [BLOCKED:2]  Priority: MEDIUM
  5. Find similar issues       [BLOCKED:3]  Priority: MEDIUM
  6. Technical reasoning       [BLOCKED:4]  Priority: CRITICAL
  7. Generate resolution      [BLOCKED:6]  Priority: CRITICAL
```

**Execution Coordinator** executes each step via existing capabilities.

## Components

| Component | Responsibility |
|-----------|----------------|
| `planner.py` | Main CPE orchestrator |
| `goal_analyzer.py` | Analyzes user intent |
| `task_decomposer.py` | Decomposes goals into tasks |
| `dependency_resolver.py` | Resolves task dependencies |
| `plan_builder.py` | Builds execution plans |
| `types.py` | Types and models |
| `metrics.py` | Performance metrics |
| `events.py` | Event publishing |

## Goal Types

- **DIAGNOSIS**: Identify problems
- **TREATMENT**: Recommend treatments
- **MONITORING**: Track and observe
- **ANALYSIS**: Analyze data
- **RESEARCH**: Find information
- **TROUBLESHOOTING**: Fix issues
- **CONSULTATION**: Provide advice
- **REPORT**: Generate reports
- **CUSTOM**: Other tasks

## Task Types

- **query**: Memory/database queries
- **retrieval**: Knowledge base search
- **reasoning**: LLM reasoning
- **diagnostic**: Device diagnostics
- **analysis**: Data analysis

## Usage

```python
from core.planning import CognitivePlanningEngine, get_planning_engine

# Get engine
engine = get_planning_engine()

# Create plan
plan = engine.plan(
    user_intent="The Philips MX450 monitor won't turn on",
    context={"device_id": "philips-mx450"},
)

# Execute via Execution Coordinator
for task in plan.tasks:
    if task.status == "ready":
        result = executor.execute(task)
        engine.update_plan_progress(plan, task.task_id, result)

print(f"Progress: {plan.progress * 100:.0f}%")
print(f"Status: {plan.status}")
```

## Output: ExecutionPlan

```python
@dataclass
class ExecutionPlan:
    plan_id: str
    goal: Goal
    tasks: list[Task]
    status: PlanStatus
    total_estimated_time_seconds: float
    total_estimated_cost: float
    total_estimated_tokens: int
    completed_tasks: int
    failed_tasks: int
    
    @property
    def progress(self) -> float: ...
    @property
    def is_complete(self) -> bool: ...
```

## Task Model

```python
@dataclass
class Task:
    task_id: str
    name: str
    description: str
    task_type: str
    capability: str
    status: TaskStatus
    priority: TaskPriority
    depends_on: list[str]
    estimated_time_seconds: float
    estimated_cost: float
```

## Integration

```
User Intent
        │
        ▼
Goal Analyzer → GoalAnalysis
        │
        ▼
Task Decomposer → [Task1, Task2, Task3]
        │
        ▼
Dependency Resolver → Ordered Tasks
        │
        ▼
Plan Builder → ExecutionPlan
        │
        ▼
Execution Coordinator
        │
        ▼
Task Executor
```

## Events

Published via Event Bus:

- `PLANNING_STARTED`
- `GOAL_ANALYZED`
- `TASKS_DECOMPOSED`
- `DEPENDENCIES_RESOLVED`
- `PLAN_BUILT`
- `PLAN_VALIDATED`
- `PLAN_READY`
- `PLAN_EXECUTING`
- `TASK_STARTED`
- `TASK_COMPLETED`
- `TASK_FAILED`
- `PLAN_COMPLETED`
- `PLAN_FAILED`

## Metrics

- Plans created/completed/failed
- Average planning time
- Tasks per plan
- Success rate
- By goal type

---

*LLM responds. Planning Engine decides what to do.*
