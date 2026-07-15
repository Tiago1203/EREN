# Architecture Validation Checklist

## Purpose

This document validates that Epic 0 architecture decisions work in practice.
Each check requires **objective evidence**, not just code existence.

---

## Epic 1 Progress: 35%

### Status Legend
- [ ] **Pending** - Not yet implemented
- [~] **Code Exists** - Implementation exists but not validated
- [x] **Validated** - Has passing tests and/or manual verification

---

## Vertical Slice: Create Patient

### Authentication Contract [~]
- [ ] `AuthenticationProvider.verify_token()` implemented
- [ ] JWT validated on every request (except public paths)
- [ ] Invalid/expired JWT returns 401
- [ ] Principal extracted from token
- [ ] **Evidence needed**: Integration test with real Supabase JWT

### Authorization Contract [ ]
- [ ] RBAC not yet implemented (planned for next milestone)
- [ ] Currently: all authenticated users can create patients

### Tenant Resolution [~]
- [ ] `tenant_id` extracted from JWT claims
- [ ] `tenant_id` present in request context
- [ ] All queries filter by `tenant_id`
- [ ] Cross-tenant access prevented
- [ ] **Evidence needed**: Cross-tenant test (see tests/integration)

### Audit [~]
- [ ] Every request generates audit entry
- [ ] PHI paths (`/patients`) are flagged
- [ ] Audit includes: principal_id, action, timestamp, correlation_id
- [ ] **Evidence needed**: Audit record persisted and queryable

### Event Architecture [~]
- [ ] `PatientCreated` event published via outbox
- [ ] Event includes: aggregate_id, event_type, tenant_id, correlation_id
- [ ] Outbox pattern ensures reliability
- [ ] **Evidence needed**: Outbox query returning PatientCreated

### Error Catalog [~]
- [ ] Error codes follow catalog (PAT-*, AUTH-*)
- [ ] HTTP status codes are appropriate
- [ ] **Evidence needed**: Error handling test

### Ubiquitous Language [~]
- [ ] `Patient` used correctly (not `PatientEntity`, `PatientRecord`)
- [ ] `Principal` used for authenticated identity
- [ ] `Tenant` used for hospital/organization

### Architecture Principles [~]
- [ ] P1: Patient Safety - HIPAA audit trail present
- [ ] P3: PHI Protected - tenant isolation working
- [ ] P4: PHI Audited - every PHI access logged
- [ ] P6: Services Own Data - Patient context owns Patient
- [ ] P7: Fail Safely - graceful error handling

---

## Test Coverage

### Unit Tests [x]
- [x] `test_create_patient_returns_patient`
- [x] `test_create_patient_calls_repository`
- [x] `test_create_patient_calls_event_bus`
- [x] `test_get_patient_returns_patient`
- [x] `test_get_patient_returns_none_when_not_found`
- [x] `test_delete_patient_returns_true_on_success`
- [x] `test_delete_patient_returns_false_when_not_found`
- [x] `test_delete_patient_publishes_event`
- [x] `test_list_patients_returns_tuple`

### Integration Tests (require PostgreSQL) [ ]
- [ ] `test_create_patient_persists_to_db`
- [ ] `test_tenant_a_cannot_see_tenant_b_data`
- [ ] `test_event_published_to_outbox`
- [ ] `test_soft_delete_only_affects_tenant`

---

## Honest Status

| Aspect | Status | Evidence Required |
|--------|--------|-------------------|
| Code exists | [x] | Yes |
| Unit tests pass | [x] | 9/9 passing |
| Integration tests | [ ] | Need PostgreSQL |
| Manual demo | [ ] | Need running app |
| CI passing | [ ] | GitHub Actions |

---

## Next Steps

Before Diagnosis Context:

1. [x] CI pipeline created
2. [x] Unit tests created (9 passing)
3. [ ] Integration tests (need PostgreSQL)
4. [ ] Manual demo
5. [ ] Cross-tenant isolation verified
6. [ ] Outbox persistence verified
7. [ ] PR #96 merged

---

*Last updated: 2026-07-15*
*Status: Code exists, tests pass, validation in progress*
