# EREN - Especificación Técnica Completa
## Fase 7: Persistence

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  

---

## Tabla de Contenidos

1. [Database Strategy](#1-database-strategy)
2. [Schema Design](#2-schema-design)
3. [Incident Tables](#3-incident-tables)
4. [Device Tables](#4-device-tables)
5. [Recommendation Tables](#5-recommendation-tables)
6. [Knowledge Tables](#6-knowledge-tables)
7. [Indexes & Performance](#7-indexes--performance)
8. [Multi-tenancy Strategy](#8-multi-tenancy-strategy)
9. [Soft Delete & Auditing](#9-soft-delete--auditing)

---

## 1. DATABASE STRATEGY

### 1.1 Technology

```
Primary: PostgreSQL 16+
  - JSONB for flexible schemas
  - Full-text search
  - Window functions for analytics
  - Row-level security for multi-tenancy

Extensions:
  - pg_trgm: Fuzzy text search
  - uuid-ossp: UUID generation
  - pg_stat_statements: Query analysis
  - pg_partman: Table partitioning

ORM: SQLAlchemy 2.0 (async)
  - Type-safe queries
  - Async support
  - Event-driven
```

### 1.2 Connection Strategy

```
Connection Pool:
  - Min connections: 10
  - Max connections: 100
  - Idle timeout: 300s
  - Max overflow: 20
  - Pool timeout: 30s

Read Replicas: 2 (for reporting)
  - All SELECT queries go to replicas
  - Writes go to primary
```

---

## 2. SCHEMA DESIGN

### 2.1 Common Fields

```sql
-- Every table includes these columns
CREATE TABLE common_fields (
    -- Primary key (override per table)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL,
    
    -- Optimistic locking
    version INT NOT NULL DEFAULT 1,
    
    -- Audit trail
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    
    -- Soft delete
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Constraints
    CONSTRAINT no_future_created CHECK (created_at <= NOW()),
    CONSTRAINT no_future_updated CHECK (updated_at <= NOW()),
    CONSTRAINT deleted_after_created CHECK (
        deleted_at IS NULL OR deleted_at >= created_at
    ),
    CONSTRAINT deleted_after_updated CHECK (
        deleted_at IS NULL OR deleted_at >= updated_at
    )
);
```

### 2.2 Schema Naming

```
Tables: snake_case, plural
  - incidents
  - devices
  - recommendations
  - knowledge_articles
  - outbox

Columns: snake_case
  - incident_id
  - created_at
  - tenant_id

Indexes: idx_{table}_{columns}
  - idx_incidents_tenant_status
  - idx_incidents_created_at

Constraints: chk_{table}_{description}
  - chk_incidents_valid_priority
```

---

## 3. INCIDENT TABLES

### 3.1 Core Tables

```sql
-- Incidents
CREATE TABLE incidents (
    -- Common fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Identity
    article_number VARCHAR(20) NOT NULL,  -- INC-2024-00001
    
    -- Content
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    
    -- Classification
    status VARCHAR(50) NOT NULL DEFAULT 'REPORTED',
    priority VARCHAR(50) NOT NULL DEFAULT 'P3_MEDIUM',
    safety_level VARCHAR(50) NOT NULL DEFAULT 'CLASS_B',
    category VARCHAR(100) NOT NULL,
    patient_impact VARCHAR(50),
    
    -- Device link
    device_id UUID,  -- FK to devices
    device_name VARCHAR(200),
    device_location VARCHAR(500),
    
    -- Temporal
    occurred_at TIMESTAMPTZ NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    
    -- Assignment
    reported_by UUID NOT NULL,
    assigned_to UUID,
    
    -- Resolution
    resolution_type VARCHAR(100),
    resolution_summary TEXT,
    resolution_details TEXT,
    resolution_verified_by UUID,
    resolution_verified_at TIMESTAMPTZ,
    downtime_minutes INT DEFAULT 0,
    
    -- SLA
    sla_target_at TIMESTAMPTZ,
    sla_breached_at TIMESTAMPTZ,
    was_sla_met BOOLEAN,
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    correlation_id UUID,
    
    -- Relationships
    related_incident_ids UUID[] DEFAULT '{}',
    
    -- Optimistic locking
    CONSTRAINT chk_incidents_valid_status CHECK (
        status IN ('REPORTED', 'TRIAGED', 'ACTIVE', 'ESCALATED', 'RESOLVED', 'CLOSED')
    ),
    CONSTRAINT chk_incidents_valid_priority CHECK (
        priority IN ('P1_CRITICAL', 'P2_HIGH', 'P3_MEDIUM', 'P4_LOW')
    )
);

-- Symptoms
CREATE TABLE incident_symptoms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    incident_id UUID NOT NULL REFERENCES incidents(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Content
    description TEXT NOT NULL,
    category VARCHAR(100),
    severity VARCHAR(50),
    frequency VARCHAR(50),
    first_observed_at TIMESTAMPTZ,
    last_observed_at TIMESTAMPTZ,
    reproducible BOOLEAN DEFAULT FALSE,
    workarounds TEXT[],
    
    -- Ordering
    symptom_order INT NOT NULL DEFAULT 0
);

-- Actions taken
CREATE TABLE incident_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    incident_id UUID NOT NULL REFERENCES incidents(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Content
    action_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    assigned_to UUID,
    due_date TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    priority VARCHAR(50),
    completed_at TIMESTAMPTZ,
    outcome VARCHAR(100),
    
    -- Ordering
    action_order INT NOT NULL DEFAULT 0
);

-- Investigation findings
CREATE TABLE investigation_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    incident_id UUID NOT NULL REFERENCES incidents(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Content
    finding_type VARCHAR(100),
    description TEXT NOT NULL,
    severity VARCHAR(50),
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    discovered_by UUID NOT NULL
);

-- Incident timeline (audit log)
CREATE TABLE incident_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    incident_id UUID NOT NULL REFERENCES incidents(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Content
    event_type VARCHAR(100) NOT NULL,
    description TEXT,
    actor_id UUID,
    actor_name VARCHAR(200),
    metadata JSONB DEFAULT '{}',
    
    -- Ordering
    event_order INT NOT NULL DEFAULT 0
);
```

---

## 4. DEVICE TABLES

```sql
-- Devices
CREATE TABLE devices (
    -- Common fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Identity
    article_number VARCHAR(20) NOT NULL UNIQUE,  -- DEV-2024-00001
    serial_number VARCHAR(100) NOT NULL,
    
    -- Classification
    device_type VARCHAR(100) NOT NULL,
    device_type_category VARCHAR(50) NOT NULL,
    risk_class VARCHAR(50) NOT NULL DEFAULT 'CLASS_B',
    name VARCHAR(200) NOT NULL,
    
    -- Manufacturer
    manufacturer_name VARCHAR(200) NOT NULL,
    manufacturer_model VARCHAR(100) NOT NULL,
    manufacturing_date DATE,
    country_of_origin VARCHAR(3),
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'REGISTERED',
    
    -- Location
    building VARCHAR(100),
    floor VARCHAR(20),
    room VARCHAR(50),
    department VARCHAR(100),
    full_address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Installation & warranty
    installation_date DATE,
    warranty_expiry DATE,
    
    -- Network
    ip_address INET,
    mac_address VARCHAR(17),
    hostname VARCHAR(100),
    
    -- Operational
    usage_hours DECIMAL(10, 2) DEFAULT 0,
    uptime_percentage DECIMAL(5, 2) DEFAULT 100.00,
    last_maintenance_at TIMESTAMPTZ,
    next_maintenance_at TIMESTAMPTZ,
    last_calibration_at TIMESTAMPTZ,
    next_calibration_at TIMESTAMPTZ,
    
    -- Hierarchy
    parent_device_id UUID REFERENCES devices(id),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    notes TEXT,
    
    -- Constraints
    CONSTRAINT chk_devices_valid_status CHECK (
        status IN ('REGISTERED', 'ACTIVE', 'CALIBRATION_DUE', 
                   'IN_MAINTENANCE', 'OUT_OF_SERVICE', 'DECOMMISSIONED')
    ),
    CONSTRAINT chk_devices_valid_risk_class CHECK (
        risk_class IN ('CLASS_A', 'CLASS_B', 'CLASS_C', 'CLASS_D')
    ),
    CONSTRAINT chk_devices_serial_unique UNIQUE (tenant_id, serial_number)
        -- Exclude deleted
        INCLUDING WHERE (deleted_at IS NULL)
);

-- Device connections
CREATE TABLE device_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    device_id UUID NOT NULL REFERENCES devices(id),
    connected_device_id UUID NOT NULL REFERENCES devices(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    connection_type VARCHAR(100),
    bidirectional BOOLEAN DEFAULT FALSE,
    
    CONSTRAINT chk_no_self_reference CHECK (device_id != connected_device_id)
);

-- Maintenance records
CREATE TABLE maintenance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    device_id UUID NOT NULL REFERENCES devices(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT,
    performed_by UUID NOT NULL,
    performed_at TIMESTAMPTZ NOT NULL,
    duration_hours DECIMAL(6, 2),
    outcome VARCHAR(100),
    parts_replaced JSONB DEFAULT '[]',
    tools_used TEXT[],
    work_order_id VARCHAR(50),
    cost DECIMAL(10, 2),
    notes TEXT
);
```

---

## 5. RECOMMENDATION TABLES

```sql
-- Recommendations
CREATE TABLE recommendations (
    -- Common fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Identity
    article_number VARCHAR(20) NOT NULL,  -- REC-2024-00001
    
    -- Context
    incident_id UUID REFERENCES incidents(id),
    device_ids UUID[] DEFAULT '{}',
    
    -- Content
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    urgency VARCHAR(50) NOT NULL DEFAULT 'NORMAL',
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'GENERATED',
    
    -- Confidence
    confidence_value DECIMAL(4, 3) NOT NULL,  -- 0.000-1.000
    confidence_level VARCHAR(50) NOT NULL,
    confidence_breakdown JSONB,
    
    -- Generation
    generated_by VARCHAR(100) NOT NULL,
    generation_method VARCHAR(100) NOT NULL,
    prompt_version VARCHAR(50),
    model_version VARCHAR(50),
    
    -- Explanation
    reasoning_chain JSONB NOT NULL,
    explanation JSONB NOT NULL,
    safety_classification JSONB,
    
    -- Actions
    actions JSONB NOT NULL DEFAULT '[]',
    contraindications JSONB DEFAULT '[]',
    
    -- Evidence & sources
    evidence JSONB NOT NULL DEFAULT '[]',
    sources JSONB NOT NULL DEFAULT '[]',
    citations JSONB DEFAULT '[]',
    
    -- Knowledge links
    knowledge_article_ids UUID[] DEFAULT '{}',
    
    -- Acceptance/rejection
    accepted_by UUID,
    accepted_at TIMESTAMPTZ,
    accepted_reason TEXT,
    rejected_by UUID,
    rejected_at TIMESTAMPTZ,
    rejection_reason VARCHAR(100),
    rejection_details TEXT,
    
    -- Feedback
    feedback JSONB,
    
    -- Outcome
    outcome JSONB,
    execution_started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Expiration
    expires_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    CONSTRAINT chk_recommendations_valid_status CHECK (
        status IN ('GENERATED', 'PENDING', 'ACCEPTED', 'REJECTED', 
                   'ACTIVE', 'COMPLETED', 'EXPIRED', 'CANCELLED')
    )
);

-- Recommendation feedback
CREATE TABLE recommendation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    recommendation_id UUID NOT NULL REFERENCES recommendations(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    rating INT CHECK (rating >= 1 AND rating <= 5),
    was_accurate BOOLEAN,
    was_actionable BOOLEAN,
    was_safe BOOLEAN,
    was_timely BOOLEAN,
    comments TEXT,
    what_was_wrong TEXT,
    what_was_right TEXT,
    alternative_action_taken TEXT,
    outcome_confirmed BOOLEAN
);
```

---

## 6. KNOWLEDGE TABLES

```sql
-- Knowledge articles
CREATE TABLE knowledge_articles (
    -- Common fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    -- Identity
    article_number VARCHAR(20) NOT NULL UNIQUE,  -- KB-00001
    title VARCHAR(300) NOT NULL,
    summary VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    content_format VARCHAR(50) NOT NULL DEFAULT 'MARKDOWN',
    
    -- Classification
    category VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    tags TEXT[] DEFAULT '{}',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    
    -- Device links
    device_ids UUID[] DEFAULT '{}',
    device_types VARCHAR(100)[] DEFAULT '{}',
    incident_type_tags TEXT[] DEFAULT '{}',
    
    -- Authorship
    author_id UUID NOT NULL,
    author_name VARCHAR(200) NOT NULL,
    reviewer_id UUID,
    
    -- Review
    review_workflow JSONB,
    review_info JSONB,
    approval_workflow JSONB,
    
    -- Quality metrics
    view_count INT DEFAULT 0,
    unique_viewers INT DEFAULT 0,
    helpful_count INT DEFAULT 0,
    not_helpful_count INT DEFAULT 0,
    bookmark_count INT DEFAULT 0,
    feedback_count INT DEFAULT 0,
    average_rating DECIMAL(3, 2),
    quality_score DECIMAL(3, 2),
    helpfulness_ratio DECIMAL(3, 2),
    search_impressions INT DEFAULT 0,
    click_through_rate DECIMAL(5, 4),
    last_accessed_at TIMESTAMPTZ,
    
    -- Content metadata
    reading_time_minutes INT DEFAULT 0,
    difficulty_level VARCHAR(50) DEFAULT 'INTERMEDIATE',
    content_hash VARCHAR(64),  -- SHA-256
    last_content_review_at TIMESTAMPTZ,
    word_count INT DEFAULT 0,
    has_video BOOLEAN DEFAULT FALSE,
    has_attachments BOOLEAN DEFAULT FALSE,
    
    -- Publication
    effective_date TIMESTAMPTZ,
    expiration_date TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    
    -- Versioning
    supersedes UUID REFERENCES knowledge_articles(id),
    superseded_by UUID REFERENCES knowledge_articles(id),
    content_version INT DEFAULT 1,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    custom_fields JSONB DEFAULT '{}',
    
    CONSTRAINT chk_articles_valid_status CHECK (
        status IN ('DRAFT', 'IN_REVIEW', 'APPROVED', 'PUBLISHED', 
                   'ARCHIVED', 'DEPRECATED')
    )
);

-- Article references
CREATE TABLE article_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    article_id UUID NOT NULL REFERENCES knowledge_articles(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    reference_type VARCHAR(100) NOT NULL,
    reference_id VARCHAR(500) NOT NULL,
    title VARCHAR(300),
    description TEXT,
    url TEXT,
    page_reference VARCHAR(100),
    is_critical BOOLEAN DEFAULT FALSE,
    access_restricted BOOLEAN DEFAULT FALSE
);

-- Article translations
CREATE TABLE article_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    article_id UUID NOT NULL REFERENCES knowledge_articles(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    language VARCHAR(10) NOT NULL,
    title VARCHAR(300),
    summary VARCHAR(500),
    body TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    translator_id UUID
);

-- Article attachments
CREATE TABLE article_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    article_id UUID NOT NULL REFERENCES knowledge_articles(id),
    tenant_id UUID NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by UUID,
    
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(100),
    file_size_bytes BIGINT,
    s3_key VARCHAR(500) NOT NULL,
    content_hash VARCHAR(64),
    is_image BOOLEAN DEFAULT FALSE,
    display_order INT DEFAULT 0
);
```

---

## 7. INDEXES & PERFORMANCE

### 7.1 Indexes for Incidents

```sql
-- Primary lookups
CREATE INDEX idx_incidents_tenant_id ON incidents(tenant_id);
CREATE INDEX idx_incidents_article_number ON incidents(article_number);
CREATE INDEX idx_incidents_tenant_status ON incidents(tenant_id, status);
CREATE INDEX idx_incidents_tenant_priority ON incidents(tenant_id, priority);
CREATE INDEX idx_incidents_tenant_created ON incidents(tenant_id, created_at DESC);

-- Device relationship
CREATE INDEX idx_incidents_device_id ON incidents(device_id) 
    WHERE device_id IS NOT NULL AND deleted_at IS NULL;
CREATE INDEX idx_incidents_tenant_device ON incidents(tenant_id, device_id) 
    WHERE device_id IS NOT NULL AND deleted_at IS NULL;

-- Assignment
CREATE INDEX idx_incidents_assigned_to ON incidents(assigned_to) 
    WHERE assigned_to IS NOT NULL AND deleted_at IS NULL;
CREATE INDEX idx_incidents_tenant_assigned ON incidents(tenant_id, assigned_to) 
    WHERE assigned_to IS NOT NULL AND deleted_at IS NULL;

-- SLA tracking
CREATE INDEX idx_incidents_sla_breach ON incidents(tenant_id, sla_target_at) 
    WHERE sla_breached_at IS NULL AND deleted_at IS NULL AND status IN ('ACTIVE', 'ESCALATED');

-- Text search
CREATE INDEX idx_incidents_title_search ON incidents 
    USING gin(title gin_trgm_ops);
CREATE INDEX idx_incidents_description_search ON incidents 
    USING gin(description gin_trgm_ops);

-- Tags
CREATE INDEX idx_incidents_tags ON incidents USING gin(tags);

-- Soft delete performance
CREATE INDEX idx_incidents_deleted ON incidents(tenant_id, deleted_at) 
    WHERE deleted_at IS NOT NULL;
```

### 7.2 Composite Indexes for Common Queries

```sql
-- Query: Active incidents by priority for a tenant
CREATE INDEX idx_incidents_active_priority ON incidents(tenant_id, priority, created_at)
    WHERE status IN ('ACTIVE', 'ESCALATED', 'TRIAGED') AND deleted_at IS NULL;

-- Query: My assigned incidents
CREATE INDEX idx_incidents_my_assigned ON incidents(tenant_id, assigned_to, status, updated_at DESC)
    WHERE deleted_at IS NULL;

-- Query: Incidents for a device
CREATE INDEX idx_incidents_device_status ON incidents(device_id, status, created_at DESC)
    WHERE deleted_at IS NULL;

-- Query: Overdue incidents
CREATE INDEX idx_incidents_overdue ON incidents(tenant_id, priority, occurred_at)
    WHERE status IN ('ACTIVE', 'ESCALATED') AND deleted_at IS NULL
      AND occurred_at < NOW() - INTERVAL '1 day' * (
          CASE priority 
              WHEN 'P1_CRITICAL' THEN 4 
              WHEN 'P2_HIGH' THEN 24 
              WHEN 'P3_MEDIUM' THEN 72 
              ELSE 168 
          END
      );
```

---

## 8. MULTI-TENANCY STRATEGY

### 8.1 Row-Level Security

```sql
-- Enable RLS on all tables
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_articles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for incidents
CREATE POLICY tenant_isolation_incidents ON incidents
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

-- Application sets tenant context
-- PostgreSQL connection sets: SET app.tenant_id = 'uuid';
```

### 8.2 Tenant Validation

```sql
-- Function to validate tenant access
CREATE OR REPLACE FUNCTION validate_tenant_access(
    p_tenant_id UUID,
    p_user_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_tenant_count INT;
BEGIN
    SELECT COUNT(*) INTO v_tenant_count
    FROM tenants
    WHERE id = p_tenant_id
      AND deleted_at IS NULL;
    
    RETURN v_tenant_count > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 9. SOFT DELETE & AUDITING

### 9.1 Soft Delete Pattern

```sql
-- All deletes are soft deletes
-- No hard deletes in the application

-- Soft delete trigger
CREATE OR REPLACE FUNCTION soft_delete_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deleted_at = NOW();
    NEW.deleted_by = current_setting('app.user_id', TRUE)::UUID;
    NEW.updated_at = NOW();
    NEW.updated_by = current_setting('app.user_id', TRUE)::UUID;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_incidents_soft_delete
    BEFORE UPDATE ON incidents
    FOR EACH ROW
    WHEN (NEW.deleted_at IS DISTINCT FROM OLD.deleted_at)
    EXECUTE FUNCTION soft_delete_trigger();

-- Query pattern for active records
CREATE OR REPLACE FUNCTION get_active_incidents(p_tenant_id UUID)
RETURNS SETOF incidents AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM incidents
    WHERE tenant_id = p_tenant_id
      AND deleted_at IS NULL
    ORDER BY created_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- Query pattern for deleted records
CREATE OR REPLACE FUNCTION get_deleted_incidents(p_tenant_id UUID)
RETURNS SETOF incidents AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM incidents
    WHERE tenant_id = p_tenant_id
      AND deleted_at IS NOT NULL
    ORDER BY deleted_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;
```

### 9.2 Audit Log

```sql
-- Audit log table (immutable)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    tenant_id UUID NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Who
    user_id UUID,
    user_name VARCHAR(200),
    session_id UUID,
    ip_address INET,
    
    -- What
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,  -- INSERT, UPDATE, DELETE, SOFT_DELETE
    table_name VARCHAR(100) NOT NULL,
    
    -- Change details
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    
    -- Context
    correlation_id UUID,
    reason TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Audit log indexes
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_tenant_time ON audit_log(tenant_id, occurred_at DESC);
CREATE INDEX idx_audit_user ON audit_log(user_id, occurred_at DESC);

-- Audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_old_values JSONB;
    v_new_values JSONB;
    v_changed_fields TEXT[];
    v_action VARCHAR(50);
BEGIN
    IF TG_OP = 'INSERT' THEN
        v_action = 'INSERT';
        v_old_values = NULL;
        v_new_values = to_jsonb(NEW);
    ELSIF TG_OP = 'UPDATE' THEN
        v_action = 'UPDATE';
        v_old_values = to_jsonb(OLD);
        v_new_values = to_jsonb(NEW);
        v_changed_fields = ARRAY(
            SELECT key
            FROM jsonb_each_text(v_new_values) AS e(key, value)
            WHERE v_old_values -> key IS DISTINCT FROM value
        );
    ELSIF TG_OP = 'DELETE' THEN
        v_action = 'DELETE';
        v_old_values = to_jsonb(OLD);
        v_new_values = NULL;
    END IF;
    
    -- Skip soft delete tracking (already in deleted_at)
    IF TG_TABLE_NAME LIKE '%_versions' THEN
        RETURN NEW;
    END IF;
    
    INSERT INTO audit_log (
        tenant_id, user_id, entity_type, entity_id,
        action, table_name, old_values, new_values, changed_fields
    ) VALUES (
        COALESCE(NEW.tenant_id, OLD.tenant_id),
        NULLIF(current_setting('app.user_id', TRUE), '')::UUID,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        v_action,
        TG_TABLE_NAME,
        v_old_values,
        v_new_values,
        v_changed_fields
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply audit to key tables
CREATE TRIGGER trg_incidents_audit
    AFTER INSERT OR UPDATE OR DELETE ON incidents
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

---

*Documento generado para implementación. Fase 7 completa.*
