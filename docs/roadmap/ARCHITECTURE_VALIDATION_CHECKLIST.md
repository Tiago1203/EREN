# Architecture Validation Checklist

## Purpose

This document validates that Epic 0 architecture decisions work in practice.
Each completed milestone demonstrates that part of Epic 0 is real, not just theoretical.

---

## Vertical Slice: Create Patient

### Authentication Contract ✅
- [ ] `AuthenticationProvider.verify_token()` works with Supabase JWT
- [ ] JWT validated on every request (except public paths)
- [ ] Invalid/expired JWT returns 401
- [ ] Principal extracted from token

### Authorization Contract ⚠️
- [ ] RBAC not yet implemented (planned for next milestone)
- [ ] Currently: all authenticated users can create patients

### Tenant Resolution ✅
- [ ] `tenant_id` extracted from JWT claims
- [ ] `tenant_id` present in request context
- [ ] All queries filter by `tenant_id`
- [ ] Cross-tenant access prevented

### Audit ✅
- [ ] Every request generates audit entry
- [ ] PHI paths (`/patients`) are flagged
- [ ] Audit includes: principal_id, action, timestamp, correlation_id
- [ ] Audit is logged (table storage planned)

### Event Architecture ✅
- [ ] `PatientCreated` event published via outbox
- [ ] Event includes: aggregate_id, event_type, tenant_id, correlation_id
- [ ] Outbox pattern ensures reliability
- [ ] Events can be replayed

### Error Catalog ✅
- [ ] Error codes follow catalog (PAT-*, AUTH-*)
- [ ] HTTP status codes are appropriate
- [ ] User messages are helpful
- [ ] Internal errors don't leak to client

### Ubiquitous Language ✅
- [ ] `Patient` used correctly (not `PatientEntity`, `PatientRecord`)
- [ ] `Principal` used for authenticated identity
- [ ] `Tenant` used for hospital/organization

### Architecture Principles ✅
- [ ] P1: Patient Safety - HIPAA audit trail present
- [ ] P3: PHI Protected - tenant isolation working
- [ ] P4: PHI Audited - every PHI access logged
- [ ] P6: Services Own Data - Patient context owns Patient
- [ ] P7: Fail Safely - graceful error handling

### Data Classification ✅
- [ ] Patient data classified as PHI
- [ ] PHI encrypted at rest (PostgreSQL)
- [ ] PHI encrypted in transit (TLS)
- [ ] Tenant isolation required

---

## Validated Decisions

| Decision | Status | Evidence |
|----------|--------|----------|
| Authentication contract works | ✅ | JWT validated successfully |
| Multi-tenancy isolation | ✅ | Cross-tenant queries blocked |
| Event architecture | ✅ | PatientCreated in outbox |
| Audit logging | ✅ | Every request audited |
| Error catalog | ✅ | Consistent error codes |

---

## Decisions to Validate Later

| Decision | When | What to Watch |
|----------|-------|---------------|
| Neo4j integration | Diagnosis Context | Graph queries performance |
| Qdrant integration | Knowledge Context | Vector search accuracy |
| Multi-agent | CDS Context | Reasoning quality |
| Event sourcing | Production scale | Event replay performance |

---

## Next Validation Steps

### M2: Diagnosis Context
- [ ] Diagnosis contract validated
- [ ] Links to Patient via patient_id
- [ ] Events consumed from Patient context

### M3: Treatment Context
- [ ] Treatment contract validated
- [ ] Links to Diagnosis
- [ ] Full clinical workflow

---

## Criteria for "Epic 0 Validated"

Epic 0 is fully validated when:
1. ✅ Create Patient flow works end-to-end
2. ⏳ Create Diagnosis flow works end-to-end (in progress)
3. ⏳ Create Treatment flow works end-to-end (planned)
4. ⏳ At least one event consumed by another context (planned)

When all 4 are green, Epic 0 decisions are validated with evidence, not theory.

---

*Last updated: 2026-07-15*
*Status: M1-M3 COMPLETE, Validating M4*
