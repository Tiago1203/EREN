# ADR-7002: Multi-Tenant Isolation Strategy

## Status
Accepted

## Context
EREN needs to serve multiple hospital tenants on a single deployment while guaranteeing data isolation for regulatory compliance (HIPAA, FDA).

## Decision
We adopt PostgreSQL Row-Level Security (RLS) as the primary isolation mechanism:

1. **Database-level isolation** - All tenant queries filtered by RLS policies
2. **Shared schema** - Single schema with tenant_id column
3. **Redis isolation** - Tenant-scoped cache keys with prefixes
4. **API isolation** - Middleware auto-injects tenant context
5. **Cross-tenant prevention** - Query builder enforces tenant filtering

## Consequences
### Positive
- Cost-effective multi-tenancy
- Simplified deployment and operations
- Strong isolation guarantees with RLS
- Consistent data access patterns

### Negative
- RLS performance overhead on complex queries
- Shared resources mean noisy neighbor risk
- Schema migrations more complex
- Requires careful index design per tenant
