# ADR-6002: Feature-First Project Structure

## Status
Accepted

## Context
EREN needs a scalable project structure that groups code by feature rather than by technical concern. This improves maintainability as the codebase grows.

## Decision
We adopt a feature-first structure with the following principles:
1. **Feature isolation** - Each module contains its own components, hooks, services, and types
2. **Shared layer** - Cross-cutting concerns in `modules/shared/`
3. **Co-location** - Related code stays together (components with their hooks, tests)
4. **Clear boundaries** - Features can import from shared, but not from other features directly

## Structure
```
apps/web/src/modules/
├── feature-a/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types/
│   └── pages/
├── feature-b/
│   └── ...
└── shared/
    ├── components/
    ├── hooks/
    └── lib/
```

## Consequences
### Positive
- Easier to understand feature scope
- Better code organization for large teams
- Improved maintainability
- Clear dependency graph

### Negative
- May lead to some code duplication
- Need discipline to maintain boundaries
- Shared folder can become a dumping ground
