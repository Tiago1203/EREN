# EREN Multi-Tenancy Strategy
## Decision: How EREN Handles Multiple Hospitals

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial decision |

---

## Context

EREN will serve multiple hospitals. We must decide:
1. **Tenancy Model**: How is data isolated?
2. **Tenant Identification**: How do we know which hospital data belongs to?
3. **Scalability**: How does this affect performance?

---

## Decision

**EREN uses SHARED DATABASE with TENANT ISOLATION via tenant_id on all records.**

```
┌─────────────────────────────────────────────────────────────┐
│                      SINGLE DATABASE                          │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                 TENANT TABLE                          │   │
│   │  tenant_id | name | settings | status | plan         │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                 SHARED TABLES                        │   │
│   │                                                      │   │
│   │  clinical.patient      — tenant_id + patient_id      │   │
│   │  biomedical.device    — tenant_id + device_id        │   │
│   │  hospital.bed         — tenant_id + bed_id          │   │
│   │                                                      │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tenancy Options Considered

### Option A: Database Per Tenant ❌ Rejected

```
Hospital A → Database A
Hospital B → Database B
Hospital C → Database C
```

**Pros:**
- Maximum isolation
- Easy backup/restore per tenant

**Cons:**
- 100 hospitals = 100 databases
- Schema changes require 100 migrations
- Cross-tenant analytics impossible
- Resource utilization poor

**Verdict:** Not scalable for 100+ hospitals.

---

### Option B: Schema Per Tenant ❌ Rejected

```
Database:
├── schema_a (Hospital A)
├── schema_b (Hospital B)
└── schema_c (Hospital C)
```

**Pros:**
- Good isolation
- Single database instance

**Cons:**
- PostgreSQL has schema limits (~1000)
- Still difficult schema migrations
- Cross-tenant analytics complex

**Verdict:** Better but not ideal.

---

### Option C: Shared Database + tenant_id ✅ SELECTED

```
Database:
├── tenants (registry)
└── All tables have tenant_id
```

**Pros:**
- Single database, single schema
- Easy schema migrations
- Cross-tenant analytics possible (with permissions)
- Good isolation with RLS

**Cons:**
- Requires discipline (always filter by tenant_id)
- Risk of cross-tenant data leaks if not careful
- Performance depends on indexing

**Verdict:** Best balance of scalability and simplicity.

---

## Implementation Strategy

### 1. Tenant Registry

```sql
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL, -- active, suspended, trial
    plan VARCHAR(50) NOT NULL,   -- basic, standard, enterprise
    
    -- Settings
    settings JSONB DEFAULT '{}',
    
    -- Compliance
    data_region VARCHAR(50) NOT NULL, -- us-east, eu-west, etc.
    hipaa_enabled BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Tenant ID on All Tables

```sql
-- Every table includes tenant_id
CREATE TABLE clinical.patients (
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    patient_id UUID PRIMARY KEY,
    mrn VARCHAR(50) NOT NULL,  -- Medical Record Number
    
    -- Patient data...
    demographics JSONB,
    consent_status JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Index for tenant isolation
    CONSTRAINT patient_tenant_pkey PRIMARY KEY (tenant_id, patient_id)
);

CREATE INDEX idx_patient_tenant ON clinical.patients(tenant_id);
```

### 3. Row-Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE clinical.patients ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's data
CREATE POLICY tenant_isolation ON clinical.patients
    USING (tenant_id = current_tenant_id());

-- Function to get current tenant
CREATE OR REPLACE FUNCTION current_tenant_id() RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_tenant', true), '')::UUID;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### 4. Application-Level Enforcement

```python
class TenantContext:
    """Thread-local tenant context."""
    
    tenant_id: UUID | None = None
    
    def set_tenant(self, tenant_id: UUID) -> None:
        self.tenant_id = tenant_id
        
    def require_tenant(self) -> UUID:
        if self.tenant_id is None:
            raise TenantRequiredError("Tenant context not set")
        return self.tenant_id


# In every repository
class PatientRepository:
    async def find_by_id(self, patient_id: UUID) -> Patient | None:
        tenant_id = self.tenant_context.require_tenant()
        return await self.db.fetch_one(
            """
            SELECT * FROM clinical.patients 
            WHERE tenant_id = $1 AND patient_id = $2
            """,
            tenant_id, patient_id
        )
```

### 5. Cross-Tenant Operations

```python
# Only system services can do cross-tenant operations
class CrossTenantService:
    """Services that operate across tenants."""
    
    @require_system_role()
    async def get_tenant_metrics(self, tenant_id: UUID) -> TenantMetrics:
        """Get metrics for a specific tenant."""
        
    @require_system_role()
    async def migrate_tenant(self, tenant_id: UUID, target_version: str):
        """Run migrations for specific tenant."""
        
    @require_admin_role()
    async def run_cross_tenant_report(self, report_type: str) -> Report:
        """Generate report across all tenants (anonymized)."""
```

---

## Data Isolation Guarantees

### Guaranteed Isolation

```
✅ Hospital A cannot see Hospital B's patients
✅ Hospital A cannot see Hospital B's devices
✅ Hospital A cannot see Hospital B's staff
✅ Hospital A cannot see Hospital B's audit logs
```

### Achieved Through

1. **Database Constraints**: Foreign keys to tenant table
2. **RLS Policies**: Database-level isolation
3. **Application Enforcement**: Every query filtered by tenant_id
4. **API Layer**: Tenant ID required for all endpoints
5. **Audit**: Cross-tenant access is audited

---

## Scalability Considerations

### Performance at Scale

```
Scenario: 100 hospitals, 10,000 patients each

Total Records:
- 1,000,000 patients
- 500,000 devices
- 100,000 beds
- 10,000,000 events/day

With proper indexing and partitioning:
- Query performance: < 50ms for single-tenant queries
- Cross-tenant analytics: Requires separate analytics database
```

### Indexing Strategy

```sql
-- Every table has tenant_id as leading column
CREATE INDEX idx_patients_tenant_mrn 
    ON clinical.patients(tenant_id, mrn);

CREATE INDEX idx_patients_tenant_created 
    ON clinical.patients(tenant_id, created_at DESC);

-- Partial indexes for active records
CREATE INDEX idx_devices_tenant_active 
    ON biomedical.devices(tenant_id, device_id) 
    WHERE status = 'active';
```

### Partitioning Strategy

```sql
-- Partition events by month for efficient retention
CREATE TABLE events (
    tenant_id UUID NOT NULL,
    event_id UUID NOT NULL,
    event_type VARCHAR(100),
    event_date DATE NOT NULL,
    ...
) PARTITION BY RANGE (event_date);

-- Create monthly partitions
CREATE TABLE events_2026_07 PARTITION OF events
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
```

---

## Multi-Tenant Deployment

### Development

```
Single database, single tenant (localhost)
```

### Staging

```
Single database, multiple tenants (staging tenants)
```

### Production

```
Database: PostgreSQL 16+ with connection pooling (PgBouncer)
├── Primary: Write operations
├── Replicas: Read operations
├── Backups: Daily + Point-in-time recovery
```

### Multi-Region

```
Region US:
├── Database US-East
└── Tenant allocation: US hospitals

Region EU:
├── Database EU-West
└── Tenant allocation: EU hospitals

Cross-region replication for disaster recovery
```

---

## Security Model

### Authentication Per Tenant

```
Tenant A:
├── Login via: hospital-a.eren.health
├── SSO: SAML/OKTA
└── MFA: Required

Tenant B:
├── Login via: hospital-b.eren.health
├── SSO: Azure AD
└── MFA: Optional
```

### Authorization Per Tenant

```
Each tenant has its own:
├── Roles (physician, nurse, admin)
├── Permissions
├── Policies
└── Users

BUT shared:
├── Core contracts
├── Capability implementations
└── Audit infrastructure
```

### Audit Per Tenant

```
Every tenant has isolated:
├── Audit logs
├── Access history
├── Compliance reports

System has visibility into:
├── Tenant-level metrics
├── Anonymized usage patterns
└── System health
```

---

## Migration Path

### Phase 1: Single Tenant (Current)

```
Deployment: Single hospital
No multi-tenancy needed
```

### Phase 2: Multi-Tenant Ready (v1.0)

```
Add tenant_id to all tables
Implement RLS policies
Add tenant context to application
```

### Phase 3: Multi-Tenant Production (v1.1)

```
Enable multi-tenancy
Onboard second hospital
Test isolation guarantees
```

### Phase 4: Scale (v1.2+)

```
Add connection pooling
Add read replicas
Add partitioning
Monitor performance
```

---

## Open Questions

| Question | Status | Notes |
|----------|--------|-------|
| Data residency requirements? | Open | May need per-region databases |
| Tenant-specific customizations? | Open | Feature flags or schema? |
| Tenant data export (GDPR)? | Open | Per-tenant export pipeline |
| Billing integration? | Open | Per-tenant metering |

---

## Summary

| Aspect | Decision |
|--------|----------|
| Tenancy Model | Shared database + tenant_id |
| Isolation Method | PostgreSQL RLS + Application enforcement |
| Tenant ID | UUID, required on all tables |
| Scalability | Partitioning + indexing |
| Deployment | Single DB → Multi-region when needed |
| Security | Per-tenant auth, shared contracts |

---

*EREN Multi-Tenancy Strategy v1.0*
*Architecture Board - 2026-07-15*
