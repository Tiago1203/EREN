# EREN - Especificación Técnica Completa
## Fase 9: Seguridad

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  

---

## 1. AUTHENTICATION

### 1.1 Auth Flow

```
User → Login Page → SSO/OAuth2 → Token Issue → API Requests

Token Types:
  - Access Token: JWT, 15 min expiry, contains claims
  - Refresh Token: Opaque, 7 days expiry, stored in httpOnly cookie
  - ID Token: OIDC, for user info

JWT Claims:
  - sub: user_id
  - tenant_id: hospital organization
  - roles: [biomedical_engineer, admin, ...]
  - permissions: [incidents.create, devices.read, ...]
  - exp: expiration timestamp
```

### 1.2 Supported Identity Providers

```
Primary: Azure AD (Enterprise SSO)
Secondary: Google Workspace
Development: Local auth (dev only)

Multi-factor: Required for:
  - Admin operations
  - Device decommissioning
  - Incident closure
  - Data export
```

---

## 2. AUTHORIZATION

### 2.1 RBAC Roles

```yaml
roles:
  CLINICAL_ADMIN:
    permissions:
      - incidents.*
      - devices.*
      - recommendations.*
      - knowledge.*
      - conversations.*
      - users.manage
      - settings.manage
  
  BIOMEDICAL_ENGINEER:
    permissions:
      - incidents.create
      - incidents.read
      - incidents.update (own or assigned)
      - incidents.triage
      - incidents.resolve
      - devices.read
      - devices.register
      - devices.update
      - devices.calibrate
      - recommendations.*
      - knowledge.*
      - conversations.*
  
  TECHNICIAN:
    permissions:
      - incidents.create
      - incidents.read
      - incidents.update (own reports only)
      - devices.read
      - recommendations.read
      - knowledge.read
      - conversations.*
  
  VIEWER:
    permissions:
      - incidents.read
      - devices.read
      - recommendations.read
      - knowledge.read
      - conversations.read
  
  PHYSICIAN:
    permissions:
      - incidents.read
      - incidents.update (patient_impact only)
      - recommendations.*
      - knowledge.*
      - conversations.*
```

### 2.2 Permission Matrix

```
Resource         | Admin | Engineer | Tech | Viewer | Physician |
-----------------|-------|----------|------|--------|----------|
incidents.create |   ✓   |    ✓     |  ✓   |   -    |    -     |
incidents.read   |   ✓   |    ✓     |  ✓   |   ✓    |    ✓     |
incidents.update |   ✓   |    ✓     |  own |   -    |    pt    |
incidents.delete |   ✓   |    -     |   -  |   -    |    -     |
devices.create   |   ✓   |    ✓     |   -  |   -    |    -     |
devices.read     |   ✓   |    ✓     |  ✓   |   ✓    |    -     |
devices.update   |   ✓   |    ✓     |   -  |   -    |    -     |
devices.delete   |   ✓   |    -     |   -  |   -    |    -     |
recomm.accept    |   ✓   |    ✓     |   -  |   -    |    ✓     |
knowledge.create |   ✓   |    ✓     |   -  |   -    |    -     |

pt = patient_impact field only
own = only own records
```

---

## 3. MULTI-TENANT ISOLATION

### 3.1 Isolation Strategy

```
Data Isolation: Row-Level Security (PostgreSQL)
  - tenant_id column on every table
  - RLS policies enforce tenant isolation
  - Application sets tenant context per request

Network Isolation:
  - Each tenant in separate VPC (enterprise)
  - Shared VPC with subnet isolation (standard)

Token Isolation:
  - JWT contains tenant_id claim
  - API validates tenant_id matches resource tenant_id
```

### 3.2 Tenant Validation

```
Every API request:
  1. Extract tenant_id from JWT
  2. Validate tenant exists and is active
  3. Validate tenant has not exceeded limits (users, devices)
  4. Set tenant context for database queries
  5. Include tenant_id in all database queries

Cross-tenant access: BLOCKED
  - No API allows accessing resources from other tenants
  - Internal APIs validate tenant ownership
  - Events include tenant_id and are filtered by consumer
```

---

## 4. CLINICAL SAFETY SECURITY

### 4.1 AI Safety Requirements

```
Patient Safety Critical:
  - All AI recommendations require human review for CLASS_C/D devices
  - SafetyEngine validation is mandatory, not optional
  - AI cannot make decisions that affect patient care
  - Every AI recommendation must include confidence level
  - AI must disclose it is AI-generated

Clinical Decision Support:
  - Recommendations are "suggestions", not "decisions"
  - Clinician always has final say
  - AI can suggest, human approves
  - Escalation path always available

Audit Requirements:
  - All AI inputs and outputs logged
  - Reasoning chain stored for audit
  - Feedback loop tracked
  - Model version tracked per recommendation
```

### 4.2 Prompt Injection Protection

```
Input Sanitization:
  - User input sanitized before prompt injection
  - Special characters escaped
  - Maximum input length enforced
  - No code execution from user input

Prompt Structure:
  - System prompt is immutable (not from user)
  - User input clearly demarcated
  - Context injected from validated sources
  - Output format enforced

Detection:
  - Monitor for prompt injection patterns
  - Anomaly detection on unusual inputs
  - Rate limiting per user
  - Alert on suspicious activity
```

---

## 5. AUDIT & COMPLIANCE

### 5.1 Audit Trail

```sql
-- Every significant action is logged
audit_log:
  - who (user_id, session_id)
  - what (entity_type, entity_id, action)
  - when (occurred_at, timestamp)
  - where (ip_address, user_agent)
  - context (correlation_id, tenant_id)
  - change (old_values, new_values, changed_fields)

Retention: 7 years (medical compliance)
Encryption: AES-256 at rest
Access: Restricted to compliance team
```

### 5.2 Compliance Requirements

```
GDPR:
  - Right to access: Implemented via /api/v1/users/me
  - Right to erasure: Implemented via soft delete + data export
  - Data portability: Export to JSON/CSV
  - Consent tracking: For non-essential data processing

HIPAA (if applicable):
  - PHI handling in separate encrypted store
  - Access logging for all PHI
  - Minimum necessary access principle
  - Encryption in transit and at rest

IEC 62366 (Usability):
  - User feedback collection
  - Use error tracking
  - Training material requirements

ISO 14971 (Risk Management):
  - Risk assessment for AI recommendations
  - Safety classification
  - Incident reporting workflow
```

---

## 6. SECRET MANAGEMENT

```
Secrets Storage: HashiCorp Vault
  - Database credentials
  - API keys
  - Service accounts
  - Encryption keys

Secret Rotation:
  - Automatic rotation every 90 days
  - Zero-downtime rotation
  - Audit trail for rotations

Development:
  - No secrets in code
  - .env files not committed
  - Secrets injected at runtime via secrets manager
```

---

*Documento generado para implementación. Fase 9 completa.*
