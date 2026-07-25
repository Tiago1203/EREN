# ADR-6001: Module Federation Architecture for EREN Platform

## Status
Accepted

## Context
EREN is evolving into a comprehensive platform with multiple modules (Dashboard, Equipos, Mantenimientos, KPIs, etc.). We need a strategy for code sharing, lazy loading, and independent deployment of modules.

## Decision
We adopt Module Federation for the following reasons:
1. **Independent deployments** - Each module can be deployed separately
2. **Code sharing** - Shared components can be consumed across modules
3. **Lazy loading** - Modules load on demand, improving initial load time
4. **Micro-frontends support** - Teams can work on modules independently

## Consequences
### Positive
- Faster initial page loads through lazy loading
- Teams can deploy modules independently
- Shared design system consumption
- Better runtime integration with existing Next.js app

### Negative
- Additional complexity in build configuration
- Need to manage shared dependencies versions
- Potential for runtime errors if versions mismatch

## Implementation Notes
- Use Webpack Module Federation with Next.js
- Shared dependencies: React, UI components, design system
- Each module is a separate Next.js page/route group
- Shared components in `modules/shared/`
