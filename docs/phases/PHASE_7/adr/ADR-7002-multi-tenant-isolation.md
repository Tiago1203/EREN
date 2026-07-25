# ADR-7002: Multi-Tenant Isolation Strategy

## Status
**Implemented** ✅ (Julio 2025)

## Implementation

### core/PHASE_7/tenant/isolation/row_level_security.py
- `RowLevelSecurityManager`: Generates `CREATE POLICY` SQL for all 13 protected tables
- SET tenant: `SET app.current_tenant = '{tenant_id}'`
- 13 protected tables: users, establishments, departments, equipment, patients, medical_records, maintenances, kpis, reports, notifications, audit_logs

### core/PHASE_7/tenant/isolation/query_filter.py
- `QueryFilter`: Automatic tenant filtering, raises `CrossTenantQueryError`
- Super-admin bypass: only for `is_super_admin = True`
- EPIC 1 integration: logs cross-tenant attempts

### core/PHASE_7/tenant/isolation/cache_isolation.py
- `CacheIsolation`: Key format `t:{tenant_id}:v{version}:{namespace}:{key}`
- 7 namespaces with configurable TTLs: session (24h), user (1h), equipment (5min), kpis (1min)
- `TenantRateLimiter`: sliding window rate limiting per tier

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
