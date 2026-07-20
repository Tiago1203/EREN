# EREN Error Catalog
## Standardized Error Codes and Responses

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |

---

## Purpose

This catalog defines all standard errors in EREN. Every API, service, and capability must use these error codes.

**Rule:** Never invent new error codes. Always use codes from this catalog.

---

## Error Code Format

```
{DOMAIN}-{NUMBER}
```

| Domain | Prefix | Examples |
|--------|---------|----------|
| Patient | PAT | PAT-001, PAT-002 |
| Device | DEV | DEV-001, DEV-014 |
| Authentication | AUTH | AUTH-001, AUTH-003 |
| Authorization | AUTHZ | AUTHZ-001, AUTHZ-003 |
| Session | SESS | SESS-001, SESS-002 |
| CDS | CDS | CDS-001, CDS-007 |
| Alarm | ALM | ALM-001, ALM-003 |
| Capacity | CAP | CAP-001, CAP-002 |
| System | SYS | SYS-001, SYS-002 |

---

## Patient Errors (PAT-*)

### PAT-001: Patient Not Found

```
Code: PAT-001
HTTP: 404
Severity: P2
Retry: No
Recoverable: Yes
User Message: "El paciente no fue encontrado."
Internal: "Patient {patient_id} not found in tenant {tenant_id}"
Fields: [patient_id, tenant_id]
```

### PAT-002: Patient Suspended

```
Code: PAT-002
HTTP: 403
Severity: P2
Retry: No
Recoverable: Yes (when reactivated)
User Message: "El acceso a este paciente está temporalmente suspendido."
Internal: "Patient {patient_id} suspended"
Fields: [patient_id]
```

### PAT-003: Patient Deceased

```
Code: PAT-003
HTTP: 404
Severity: P1
Retry: No
Recoverable: No
User Message: "Este paciente ha sido registrado como fallecido."
Internal: "Patient {patient_id} is deceased"
Fields: [patient_id]
```

---

## Device Errors (DEV-*)

### DEV-001: Device Not Found

```
Code: DEV-001
HTTP: 404
Severity: P2
Retry: No
Recoverable: Yes
User Message: "El dispositivo no fue encontrado."
Internal: "Device {device_id} not found"
Fields: [device_id]
```

### DEV-014: Device Offline

```
Code: DEV-014
HTTP: 503
Severity: P1
Retry: Yes (3x with backoff)
Recoverable: Yes (when device reconnects)
Safety: CRITICAL if device controls patient
User Message: "El dispositivo no está disponible temporalmente."
Internal: "Device {device_id} offline since {last_seen}"
Fields: [device_id, last_seen]
Monitoring: Alert if > 5 minutes
```

### DEV-020: Device Calibration Due

```
Code: DEV-020
HTTP: 200 (warning)
Severity: P2
Retry: N/A
Recoverable: Yes (after calibration)
User Message: "Este dispositivo requiere calibración."
Internal: "Device {device_id} calibration overdue since {due_date}"
Fields: [device_id, due_date]
```

---

## Authentication Errors (AUTH-*)

### AUTH-001: Invalid Credentials

```
Code: AUTH-001
HTTP: 401
Severity: P1
Retry: No (after lockout)
Recoverable: Yes (with valid credentials)
User Message: "Credenciales inválidas."
Internal: "Authentication failed for {email}"
Fields: [email]
Security: Log for abuse detection
```

### AUTH-002: Account Locked

```
Code: AUTH-002
HTTP: 403
Severity: P1
Retry: No
Recoverable: Yes (after unlock)
User Message: "Cuenta bloqueada por múltiples intentos fallidos."
Internal: "Account {principal_id} locked after {failed_attempts} attempts"
Fields: [principal_id, failed_attempts]
```

### AUTH-003: Token Expired

```
Code: AUTH-003
HTTP: 401
Severity: P1
Retry: No
Recoverable: Yes (with refresh token)
User Message: "Tu sesión ha expirado. Por favor inicia sesión nuevamente."
Internal: "Token expired at {expired_at}"
Fields: [expired_at]
```

---

## Authorization Errors (AUTHZ-*)

### AUTHZ-001: Access Denied

```
Code: AUTHZ-001
HTTP: 403
Severity: P1
Retry: No
Recoverable: Yes (with proper permissions)
User Message: "No tienes permiso para realizar esta acción."
Internal: "Principal {principal_id} denied {action} on {resource_type}:{resource_id}"
Fields: [principal_id, action, resource_type, resource_id]
Audit: Required
```

### AUTHZ-002: Insufficient Role

```
Code: AUTHZ-002
HTTP: 403
Severity: P2
Retry: No
Recoverable: Yes (with role upgrade)
User Message: "Se requiere un rol superior para esta acción."
Internal: "Principal {principal_id} has {current_role}, requires {required_role}"
Fields: [principal_id, current_role, required_role]
```

---

## Session Errors (SESS-*)

### SESS-001: Session Expired

```
Code: SESS-001
HTTP: 401
Severity: P1
Retry: No
Recoverable: Yes (create new session)
User Message: "Tu sesión ha expirado."
Internal: "Session {session_id} expired at {expires_at}"
Fields: [session_id]
```

### SESS-002: Session Invalid

```
Code: SESS-002
HTTP: 401
Severity: P1
Retry: No
Recoverable: Yes (create new session)
User Message: "Sesión inválida. Por favor inicia sesión nuevamente."
Internal: "Session {session_id} is invalid"
Fields: [session_id]
```

---

## CDS Errors (CDS-*)

### CDS-007: Recommendation Confidence Low

```
Code: CDS-007
HTTP: 200 (partial success)
Severity: P1
Retry: No
Recoverable: N/A
User Message: "Tengo baja confianza en esta recomendación."
Internal: "CDS confidence {confidence} below threshold"
Fields: [confidence, evidence_count]
Action: User should verify independently
```

### CDS-010: Evidence Not Found

```
Code: CDS-010
HTTP: 200 (empty result)
Severity: P2
Retry: No
Recoverable: N/A
User Message: "No encontré evidencia suficiente para esta consulta."
Internal: "No evidence found for query {query_hash}"
Fields: [query_hash]
```

### CDS-020: LLM Timeout

```
Code: CDS-020
HTTP: 503
Severity: P1
Retry: Yes (3x with backoff)
Recoverable: Yes (after retry or fallback)
User Message: "El servicio de recomendaciones está temporalmente unavailable."
Internal: "LLM request timed out after {timeout}s"
Fields: [timeout]
Fallback: Rule-based response
```

---

## Alarm Errors (ALM-*)

### ALM-001: Alarm Not Found

```
Code: ALM-001
HTTP: 404
Severity: P3
Retry: No
Recoverable: Yes
User Message: "Alarma no encontrada."
Internal: "Alarm {alarm_id} not found"
Fields: [alarm_id]
```

### ALM-003: Alarm Already Acknowledged

```
Code: ALM-003
HTTP: 409
Severity: P3
Retry: No
Recoverable: No
User Message: "Esta alarma ya fue reconocida."
Internal: "Alarm {alarm_id} already acknowledged by {acknowledged_by}"
Fields: [alarm_id, acknowledged_by]
```

---

## Capacity Errors (CAP-*)

### CAP-001: No Beds Available

```
Code: CAP-001
HTTP: 503
Severity: P1
Retry: Yes (check availability)
Recoverable: Yes (when bed available)
User Message: "No hay camas disponibles en {unit}."
Internal: "Unit {unit} at {occupancy}% capacity"
Fields: [unit, occupancy]
```

### CAP-002: Unit At Capacity

```
Code: CAP-002
HTTP: 200 (warning)
Severity: P2
Retry: N/A
Recoverable: N/A
User Message: "{unit} está cerca de su capacidad máxima."
Internal: "Unit {unit} at {occupancy}% (threshold: {threshold}%)"
Fields: [unit, occupancy, threshold]
```

---

## System Errors (SYS-*)

### SYS-001: Internal Error

```
Code: SYS-001
HTTP: 500
Severity: P0
Retry: No
Recoverable: Yes (after fix)
User Message: "Ocurrió un error interno. Por favor intenta nuevamente."
Internal: "Internal error: {error_id}"
Fields: [error_id]
Monitoring: Alert immediately
```

### SYS-002: Service Unavailable

```
Code: SYS-002
HTTP: 503
Severity: P1
Retry: Yes (with backoff)
Recoverable: Yes (when service recovers)
User Message: "El servicio no está disponible temporalmente."
Internal: "Service {service} unavailable"
Fields: [service]
Monitoring: Alert if > 1 minute
```

### SYS-003: Database Timeout

```
Code: SYS-003
HTTP: 503
Severity: P1
Retry: Yes (3x with backoff)
Recoverable: Yes (after retry or failover)
User Message: "El servicio está experimentando alta demanda."
Internal: "Database timeout after {timeout}ms"
Fields: [timeout]
Monitoring: Alert if > 3 occurrences/minute
```

---

## Error Response Format

All EREN APIs must return errors in this format:

```json
{
  "error": {
    "code": "PAT-001",
    "message": "El paciente no fue encontrado.",
    "details": {
      "patient_id": "abc-123",
      "tenant_id": "hospital-001"
    },
    "timestamp": "2026-07-15T10:30:00Z",
    "trace_id": "trace-abc-123"
  }
}
```

---

## Creating New Error Codes

1. Check if similar error exists in catalog
2. Assign code: `{DOMAIN}-{NEXT_NUMBER}`
3. Document: HTTP, severity, retry, recovery, messages
4. Add to this catalog
5. Update API documentation

---

*EREN Error Catalog v1.0*
*Architecture Board - 2026-07-15*
