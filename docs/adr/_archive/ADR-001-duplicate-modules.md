# ADR-001: Architecture Duplications Found During Audit

**Status:** Accepted  
**Date:** 2026-07-14  
**Deciders:** Architecture Review Board

---

## Context

During the architecture audit, several module duplications were identified that need resolution:

1. **workflow/ vs workflows/** - Different levels of implementation
2. **orchestration/ vs orchestrator/** - Contracts vs Implementation
3. **planning/ vs planner/** - Implementation vs Contracts
4. **diagnostic/ vs diagnostics/** - Potential duplication

## Decision Drivers

- Need for clear separation of contracts vs implementations
- Developer confusion about which module to use
- Maintenance overhead of duplicate code
- Naming consistency

## Options Considered

### Option A: Keep All (Document Differences)

Mantener todos los módulos pero documentar claramente las diferencias.

**Pros:**
- No refactoring needed
- Clear separation maintained

**Cons:**
- Confusion remains
- More modules to maintain

### Option B: Merge Implementations into Contracts

Combinar la implementación con los contratos, eliminando duplicación.

**Pros:**
- Single source of truth
- Less confusion

**Cons:**
- Larger modules
- Potential breaking changes

### Option C: Rename for Clarity

Renombrar módulos para que los nombres reflejen el propósito.

**Pros:**
- Clear naming
- Easy to understand

**Cons:**
- Breaking changes
- Git history changes

## Decision

**Option A for planning/orchestrator, Option B for workflow/**

Rationale:
- `orchestration/` vs `orchestrator/`: Keep both - different purposes (contracts vs engine)
- `planning/` vs `planner/`: Keep both - contracts vs implementation
- `workflow/` vs `workflows/`: **Merge into workflows/** - workflow/ only has stubs

## Consequences

### Positive
- Clear documentation of module purposes
- Reduced confusion
- Cleaner architecture

### Negative
- Deprecation of `workflow/` module
- Migration effort for existing users

## Compliance

This ADR must be reviewed and updated when decisions are made.

---

## References

- [Architecture Audit Report](../architecture/ARCHITECTURE_AUDIT_REPORT.md)
- [Refactoring Plan](../architecture/REFACTORING_PLAN.md)
