# Cognitive Decision Engine (CDE)

## Overview

Refactored from Planning Engine to be a complete decision-making system.

## Philosophy

> **Planning is only part of decision-making.**
> The Decision Engine decides the best strategy to achieve a cognitive goal.

**The Decision Engine NEVER:**
- Executes tasks
- Queries providers
- Uses OpenAI directly
- Consults memory
- Consults retrieval

**It ONLY:**
- Analyzes goals
- Selects strategies
- Evaluates risks
- Builds decision plans
- Manages replanning
- Takes decisions

## Architecture

```
Execution Coordinator
        │
        ▼
Cognitive Decision Engine
        │
        ├── Goal Analyzer
        │        │
        │        └──► Intent Analysis
        │        └──► Goal Type Detection
        │        └──► Risk Tolerance
        │
        ├── Planning Module
        │        │
        │        ├──► Task Decomposer
        │        └──► Dependency Resolver
        │
        ├── Strategy Selector
        │        │
        │        └──► SEQUENTIAL
        │        └──► PARALLEL
        │        └──► HYBRID
        │        └──► CONDITIONAL
        │        └──► EXPLORATORY
        │        └──► CONSERVATIVE
        │        └──► AGGRESSIVE
        │
        ├── Risk Evaluator
        │        │
        │        └──► Risk Assessment
        │        └──► Mitigation
        │        └──► Escalation
        │
        ├── Execution Policy
        │        │
        │        ├──► STRICT
        │        ├──► ADAPTIVE
        │        ├──► CONSERVATIVE
        │        ├──► AGGRESSIVE
        │        ├──► FAILFAST
        │        └──► GRACEFUL
        │
        ├── Replanner
        │        │
        │        └──► Modify plans
        │        └──► Cancel plans
        │        └──► Recreate plans
        │
        └── Decision Builder
                 │
                 └──► DecisionPlan

        ▼
DecisionPlan (Tasks)
```

## Components

| Component | Responsibility |
|-----------|----------------|
| `engine.py` | Main CDE orchestrator |
| `goal_analyzer.py` | Analyzes user intent |
| `task_decomposer.py` | Decomposes goals into tasks |
| `dependency_resolver.py` | Resolves task dependencies |
| `strategy_selector.py` | Selects optimal strategy |
| `risk_evaluator.py` | Evaluates risk levels |
| `execution_policy.py` | Defines execution rules |
| `replanner.py` | Handles plan modification |
| `decision_builder.py` | Builds decision plans |
| `types.py` | Types and models |
| `metrics.py` | Performance metrics |
| `events.py` | Event publishing |

## Decision Strategies

- **SEQUENTIAL**: Execute tasks one at a time
- **PARALLEL**: Execute independent tasks in parallel
- **HYBRID**: Mix of sequential and parallel
- **CONDITIONAL**: Based on conditions
- **EXPLORATORY**: Explore multiple paths
- **CONSERVATIVE**: Minimize risk
- **AGGRESSIVE**: Maximize speed

## Execution Policies

- **STRICT**: Follow plan exactly
- **ADAPTIVE**: Adapt to conditions
- **CONSERVATIVE**: Minimize changes
- **AGGRESSIVE**: Allow more changes
- **FAILFAST**: Stop on first failure
- **GRACEFUL**: Handle failures gracefully

## Risk Levels

- **MINIMAL**: Very low risk
- **LOW**: Low risk
- **MEDIUM**: Medium risk
- **HIGH**: High risk
- **CRITICAL**: Critical risk

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

## Usage

```python
from core.decision import CognitiveDecisionEngine, get_decision_engine

# Get engine
engine = get_decision_engine()

# Make decision
plan = engine.decide(
    user_intent="The Philips MX450 monitor won't turn on",
    context={"device_id": "philips-mx450"},
)

# Check strategy and risk
print(f"Strategy: {plan.strategy}")
print(f"Risk: {plan.overall_risk}")
print(f"Policy: {plan.policy}")
print(f"Tasks: {len(plan.tasks)}")

# Execute via Execution Coordinator
for task in plan.tasks:
    if task.status == "ready":
        result = executor.execute(task)
        engine.update_plan_progress(plan, task.task_id, result)

print(f"Progress: {plan.progress * 100:.0f}%")
print(f"Status: {plan.status}")

# Replan if needed
if plan.has_failed:
    new_plan = engine.replan(plan, "Task failed - replanning")

# Cancel if needed
cancelled = engine.cancel(plan, "User requested cancellation")
```

## Replanning

```python
# Check if replanning is needed
should_escalate, reason = engine.should_escalate(plan)

# Replan
new_plan = engine.replan(
    plan,
    reason="High failure rate",
    affected_tasks=["task-3", "task-4"],
)

# Pause/Resume
paused = engine.pause(plan)
resumed = engine.resume(plan)
```

## Decision Plan Structure

```python
@dataclass
class DecisionPlan:
    plan_id: str
    goal: Goal
    tasks: list[DecisionTask]
    strategy: DecisionStrategy
    policy: ExecutionPolicy
    status: DecisionStatus
    overall_risk: RiskLevel
    risk_factors: list[str]
    total_estimated_time_seconds: float
    completed_tasks: int
    failed_tasks: int
    replan_count: int
    
    @property
    def progress(self) -> float: ...
    @property
    def is_complete(self) -> bool: ...
```

## Events

Published via Event Bus:

- `DECISION_STARTED`
- `GOAL_ANALYZED`
- `STRATEGY_SELECTED`
- `RISK_EVALUATED`
- `TASKS_DECOMPOSED`
- `DEPENDENCIES_RESOLVED`
- `DECISION_BUILT`
- `DECISION_VALIDATED`
- `DECISION_APPROVED`
- `DECISION_READY`
- `DECISION_EXECUTING`
- `TASK_STARTED`
- `TASK_COMPLETED`
- `TASK_FAILED`
- `DECISION_COMPLETED`
- `DECISION_FAILED`
- `DECISION_REPLANNED`
- `DECISION_CANCELLED`
- `ESCALATION_REQUIRED`

## Metrics

- Decisions made/completed/failed
- Average decision time
- Tasks per decision
- Success rate
- Replan rate
- By strategy
- By goal type

---

*Planning is only part of decision-making. The Decision Engine decides the best strategy.*
