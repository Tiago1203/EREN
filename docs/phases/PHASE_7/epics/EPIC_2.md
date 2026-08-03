# EPIC 2 — Multi-Tenant Architecture

*PHASE 7 - Enterprise & Production*

## Objetivo
Implementar arquitectura multi-tenant para soportar múltiples hospitales/organizaciones en una única instancia de EREN.

## Tipo
**Core**

## Dependencias
- EPIC 0 (Compliance & Security Foundation)
- PHASE_1/infrastructure (database schema)

## Componentes
- Tenant Manager
- Tenant Isolation Middleware
- Resource Quota Manager
- Cross-Tenant Query Prevention
- Tenant Migration Tools

## Implementación

```
core/PHASE_7/tenant/
├── manager/
│   ├── tenant_manager.py           # CRUD de tenants
│   ├── tenant_context.py          # Thread-local tenant context
│   ├── tenant_resolver.py         # Resolve tenant from request
│   └── tenant_validator.py       # Tenant configuration validation
│
├── isolation/
│   ├── row_level_security.py      # PostgreSQL RLS policies
│   ├── query_filter.py            # Automatic tenant filtering
│   ├── data_isolation.py          # Tenant data boundaries
│   └── cache_isolation.py         # Redis tenant isolation
│
├── quotas/
│   ├── quota_manager.py           # Resource quotas per tenant
│   ├── usage_tracker.py           # Track resource usage
│   └── quota_enforcer.py          # Enforce limits
│
├── migrations/
│   ├── tenant_creator.py          # Create new tenant
│   ├── tenant_exporter.py         # Export tenant data
│   └── tenant_importer.py         # Import tenant data
│
└── api/
    ├── tenant_api.py              # Tenant management API
    └── admin_api.py               # Super-admin tenant controls
```

## Domain Objects
- `Tenant`
- `TenantConfig`
- `ResourceQuota`
- `TenantUsage`
- `TenantSubscription`

## Resultado
Arquitectura multi-tenant que permite múltiples hospitales en una instancia con aislamiento de datos garantizado.

## Status
- [x] **IMPLEMENTED** ✅ (Julio 2025)

## Implementación Realizada

### Manager (`core/PHASE_7/tenant/manager/`)
| Archivo | Descripción |
|---------|-------------|
| `tenant_manager.py` | CRUD completo, 5 estados, 4 subscription tiers, estadísticas |
| `tenant_context.py` | Thread-local context, async-safe, contextvars, require_tenant_context |
| `tenant_resolver.py` | Resolución por header/subdomain/path/jwt/default, TenantMiddleware |
| `tenant_validator.py` | Validación slug, HIPAA, GDPR, subscription, límites por tier |

### Isolation (`core/PHASE_7/tenant/isolation/`)
| Archivo | Descripción |
|---------|-------------|
| `row_level_security.py` | RLS policies generation, SET tenant SQL, 13 protected tables |
| `query_filter.py` | Automatic tenant filtering, CrossTenantQueryError, bypass for super_admin |
| `data_isolation.py` | DataBoundary, sanitize export, GDPR PHI redaction, import validation |
| `cache_isolation.py` | CacheKey with tenant prefix, TTL por namespace, TenantRateLimiter |

### Quotas (`core/PHASE_7/tenant/quotas/`)
| Archivo | Descripción |
|---------|-------------|
| `quota_manager.py` | 8 resource types, 4 tiers (starter/professional/enterprise/trial), alertas |
| `usage_tracker.py` | Tracking granular, daily/monthly aggregates, tendencias, UsageMetric |
| `quota_enforcer.py` | Check & consume, QuotaExceededError, decorators @enforce_quota |

### Migrations (`core/PHASE_7/tenant/migrations/`)
| Archivo | Descripción |
|---------|-------------|
| `tenant_creator.py` | 7-step setup (schema, RLS, cache, email), TenantSetupConfig |
| `tenant_exporter.py` | ExportJob, GDPR validation, estimate size, streaming JSON |
| `tenant_importer.py` | Dry-run, ID mapping (preserve/generate/map), rollback |

### API (`core/PHASE_7/tenant/api/`)
| Archivo | Descripción |
|---------|-------------|
| `tenant_api.py` | TenantAPIService (CRUD, quotas, usage), TenantMiddleware para FastAPI |
| `admin_api.py` | AdminAPIService, health checks, emergency suspend, cross-tenant reports |

## Tests
- **35 tests passing** covering all modules
- `tests/unit/PHASE_7/tenant/test_tenant.py` - TenantManager, Context, Resolver, Validator, Quotas
