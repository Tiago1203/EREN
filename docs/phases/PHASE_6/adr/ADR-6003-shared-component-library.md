# ADR-6003: Shared Component Library Strategy

## Status
Accepted

## Context
EREN needs consistent UI components across all modules. We need a strategy for building, sharing, and maintaining these components.

## Decision
We establish a shared component library located at `modules/shared/components/`:

1. **Design System Components** - Base components (Button, Input, Card)
2. **Domain Components** - Components specific to clinical engineering domain
3. **Module Components** - Cross-module reusable components

## Component Categories
```
shared/components/
├── ui/           # Design system primitives
├── layout/       # Layout components (Sidebar, Header)
├── charts/       # Chart components
├── forms/        # Form components
└── feedback/     # Loading, alerts, toasts
```

## Consequences
### Positive
- Consistent UI across all modules
- Single source of truth for design tokens
- Easy updates propagate to all modules
- Reduced duplication

### Negative
- Need versioning strategy
- Harder to customize per-module
- Must maintain backward compatibility
