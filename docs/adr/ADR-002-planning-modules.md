# ADR-002: Planning vs Planner Module Separation

**Status:** Accepted  
**Date:** 2026-07-14  
**Deciders:** Architecture Review Board

---

## Context

EREN has two planning-related modules that appear similar but serve different purposes:
- `core/planner/` - Contracts and interfaces
- `core/planning/` - Complete implementation

## Decision

**Keep both modules with clear separation of concerns.**

### core/planner/ - Contracts Layer

**Purpose:** Define interfaces and contracts that other modules depend on.

**Contains:**
- `PlannerPort` - Main interface protocol
- `Plan`, `PlanStep` - Base model definitions
- `PlannerError` and subclasses
- Stub implementations

**Used by:**
- Orchestrator (depends on `PlannerPort`)
- Decision Engine
- Workflow Engine
- Any module that needs planning capabilities

**Example:**
```python
from core.planner import PlannerPort

class Orchestrator:
    def __init__(self, planner: PlannerPort):
        self._planner = planner
```

### core/planning/ - Implementation Layer

**Purpose:** Complete cognitive planning engine implementation.

**Contains:**
- `CognitivePlanningEngine` - Main engine
- `GoalAnalyzer` - Intent analysis
- `TaskDecomposer` - Goal → Tasks
- `DependencyResolver` - Execution order
- `PlanBuilder` - Execution plans

**Example:**
```python
from core.planning import CognitivePlanningEngine

engine = CognitivePlanningEngine()
plan = engine.plan(user_intent="Fix the monitor", context={})
```

## Consequences

### Positive
- Clear dependency direction (planner → planning)
- Other modules only depend on contracts
- Easy to swap implementations
- Testability improved

### Negative
- Two modules to maintain
- Possible confusion for new developers

## Migration Path

1. New code should import from `core/planning/` for implementation
2. Code depending on contracts should import from `core/planner/`
3. Document both modules in respective READMEs

## References

- [Architecture Audit Report](../architecture/ARCHITECTURE_AUDIT_REPORT.md)
- [ADR-001](./ADR-001-duplicate-modules.md)
