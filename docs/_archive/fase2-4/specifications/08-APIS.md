# EREN - Especificación Técnica Completa
## Fase 8: APIs

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  

---

## Tabla de Contenidos

1. [API Architecture](#1-api-architecture)
2. [REST API Design](#2-rest-api-design)
3. [Internal APIs](#3-internal-apis)
4. [Request/Response DTOs](#4-requestresponse-dtos)
5. [Error Handling](#5-error-handling)
6. [Versioning Strategy](#6-versioning-strategy)

---

## 1. API ARCHITECTURE

### 1.1 API Layers

```
┌─────────────────────────────────────────────────────────┐
│                    External APIs                          │
│  - REST API (clinicians, admins)                         │
│  - WebSocket (real-time updates)                        │
│  - GraphQL (future)                                     │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  API Gateway (Kong)                       │
│  - Authentication / Authorization                         │
│  - Rate Limiting                                         │
│  - Request Logging                                       │
│  - Circuit Breaking                                       │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  Internal APIs (gRPC/HTTP)               │
│  - Service-to-service communication                       │
│  - Event-driven triggers                                  │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  Application Services                     │
│  - Commands & Queries                                     │
│  - Validation                                             │
│  - Authorization                                          │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  Domain Layer                             │
│  - Aggregates                                             │
│  - Domain Services                                       │
│  - Value Objects                                          │
└─────────────────────────────────────────────────────────┘
```

### 1.2 REST API Structure

```
/api/v1
  /incidents
    GET    /                          # List incidents
    POST   /                           # Create incident
    GET    /{incident_id}              # Get incident
    PATCH  /{incident_id}             # Update incident
    DELETE /{incident_id}             # Soft delete incident
    
    /{incident_id}
      /triage       POST              # Triage incident
      /open         POST              # Open incident
      /escalate     POST              # Escalate incident
      /resolve      POST              # Resolve incident
      /close        POST              # Close incident
      /reopen       POST              # Reopen incident
      
      /symptoms     GET, POST        # Manage symptoms
      /actions      GET, POST         # Manage actions
      /timeline     GET               # Get timeline
      /recommendations GET           # Get recommendations
      
  /devices
    GET    /                          # List devices
    POST   /                           # Register device
    GET    /{device_id}               # Get device
    PATCH  /{device_id}               # Update device
    DELETE /{device_id}               # Decommission device
    
    /{device_id}
      /activate     POST              # Activate device
      /calibrate    POST              # Record calibration
      /maintenance  POST              # Schedule/record maintenance
      /relocate     POST              # Relocate device
      /incidents    GET               # Get device incidents
      
  /recommendations
    GET    /                          # List recommendations
    GET    /{recommendation_id}      # Get recommendation
    POST   /{recommendation_id}/accept   # Accept
    POST   /{recommendation_id}/reject   # Reject
    POST   /{recommendation_id}/feedback # Submit feedback
    
  /knowledge
    GET    /                          # Search articles
    POST   /                           # Create article
    GET    /{article_id}              # Get article
    PATCH  /{article_id}               # Update article
    
    /{article_id}
      /submit-review  POST            # Submit for review
      /approve       POST              # Approve
      /publish       POST              # Publish
      /archive       POST              # Archive

  /conversations
    GET    /                          # List conversations
    POST   /                           # Start conversation
    GET    /{conversation_id}          # Get conversation
    POST   /{conversation_id}/messages POST  # Send message
    
  /internal
    /tenants/{tenant_id}
      /incidents  GET  # For internal cross-context queries
      /devices   GET  # For internal cross-context queries
```

---

## 2. REST API DESIGN

### 2.1 Incident Endpoints

```yaml
# Create Incident
POST /api/v1/incidents

Request:
  headers:
    Authorization: Bearer {token}
    Content-Type: application/json
    X-Tenant-ID: {tenant_id}
    X-Correlation-ID: {correlation_id}
  
  body:
    title: string (required, max 200)
    description: string (required, max 5000)
    priority: enum (P1_CRITICAL|P2_HIGH|P3_MEDIUM|P4_LOW)
    safety_level: enum (CLASS_A|CLASS_B|CLASS_C|CLASS_D)
    category: string (required)
    device_id: string (UUID, optional)
    device_name: string (optional)
    device_location: string (optional)
    patient_impact: enum (optional)
    occurred_at: datetime (ISO 8601)
    detected_at: datetime (ISO 8601)
    tags: string[] (optional, max 20)
    correlation_id: string (UUID, optional)

Response 201 Created:
  headers:
    X-Request-ID: {request_id}
    X-Correlation-ID: {correlation_id}
    Location: /api/v1/incidents/{incident_id}
  
  body:
    data:
      id: string (UUID)
      article_number: string (INC-2024-00001)
      title: string
      description: string
      status: REPORTED
      priority: P3_MEDIUM
      safety_level: CLASS_C
      category: HARDWARE_FAILURE
      device_id: string | null
      created_at: datetime
      created_by: string
      version: 1
    meta:
      request_id: string
      correlation_id: string

Response 400 Bad Request:
  body:
    error:
      code: VALIDATION_ERROR
      message: "Validation failed"
      details:
        - field: title
          code: REQUIRED
          message: "Title is required"
        - field: priority
          code: INVALID_ENUM
          message: "Priority must be one of..."

Response 401 Unauthorized:
  body:
    error:
      code: UNAUTHORIZED
      message: "Invalid or expired token"

Response 403 Forbidden:
  body:
    error:
      code: FORBIDDEN
      message: "User does not have permission to create incidents"
```

```yaml
# Triage Incident  
POST /api/v1/incidents/{incident_id}/triage

Request:
  headers:
    Authorization: Bearer {token}
    Content-Type: application/json
  
  body:
    priority: enum (required)
    category: string (required)
    assigned_to: string (UUID, optional)
    triage_notes: string (optional, max 2000)
    auto_open: boolean (default: false)

Response 200 OK:
  body:
    data:
      id: string
      status: TRIAGED (or ACTIVE if auto_open=true)
      priority: P2_HIGH
      category: HARDWARE_FAILURE
      assigned_to: string | null
      version: 2
    meta:
      transition: TRIAGED
      occurred_at: datetime
```

```yaml
# Search Incidents
GET /api/v1/incidents

Query Parameters:
  status: string[] (optional, repeat for multiple)
    values: REPORTED|TRIAGED|ACTIVE|ESCALATED|RESOLVED|CLOSED
  
  priority: string[] (optional)
    values: P1_CRITICAL|P2_HIGH|P3_MEDIUM|P4_LOW
  
  category: string[] (optional)
  
  device_id: string (UUID, optional)
  
  assigned_to: string (UUID, optional)
  
  date_from: datetime (optional)
  date_to: datetime (optional)
  
  q: string (optional, full-text search)
  
  sort: string (default: -created_at)
    values: created_at|priority|status|occurred_at
    prefix - for descending
  
  page: int (default: 1)
  page_size: int (default: 20, max: 100)

Response 200 OK:
  body:
    data:
      - id: string
        article_number: string
        title: string
        status: string
        priority: string
        category: string
        device_name: string | null
        assigned_to: string | null
        created_at: datetime
        occurred_at: datetime
      - ...
    pagination:
      page: 1
      page_size: 20
      total_items: 245
      total_pages: 13
      has_next: true
      has_prev: false
    meta:
      filters_applied:
        status: [ACTIVE, ESCALATED]
        priority: [P1_CRITICAL, P2_HIGH]
      sort: -created_at
```

---

## 3. INTERNAL APIS

### 3.1 Internal API Patterns

```yaml
# Internal APIs use service-to-service authentication
# Token: Shared secret or mTLS

Base URL: /api/v1/internal

Authentication:
  headers:
    X-Internal-Api-Key: {shared_secret}
    X-Tenant-ID: {tenant_id}
    X-Correlation-ID: {correlation_id}

# All internal APIs return consistent envelope
Response:
  body:
    data: { ... } | [ ... ]
    meta:
      request_id: string
      correlation_id: string
      timing_ms: int
    error: null
```

### 3.2 Internal Endpoints

```yaml
# Get Device Info (for Incident Context)
GET /api/v1/internal/tenants/{tenant_id}/devices/{device_id}

Response 200:
  body:
    data:
      device_id: string
      tenant_id: string
      device_name: string
      device_type: string
      device_type_category: string
      risk_class: CLASS_C
      status: ACTIVE
      location:
        building: string
        floor: string
        room: string
        department: string
        full_address: string
      manufacturer:
        name: string
        model: string
        serial_number: string
      calibration:
        is_current: true
        next_calibration_date: datetime
        days_until_due: 45
      maintenance:
        next_maintenance_date: datetime
        days_until_due: 30
      operational_status:
        is_operational: true
        uptime_percentage: 99.2
        has_open_incidents: false
        requires_attention: false
      version: 15
    meta:
      cached: true
      cached_at: datetime
      ttl_seconds: 30

# Search Knowledge (for Recommendation Context)
POST /api/v1/internal/tenants/{tenant_id}/knowledge/search

Request:
  body:
    query: string
    filters:
      categories: string[]
      device_types: string[]
      status: [PUBLISHED]
      language: en
      date_range:
        from: datetime
        to: datetime
    pagination:
      page: 1
      page_size: 20
    include_body_preview: true
    body_preview_length: 300

Response 200:
  body:
    data:
      - article_id: string
        article_number: KB-00042
        title: string
        summary: string
        category: TROUBLESHOOTING
        status: PUBLISHED
        tags: [mri, display, troubleshooting]
        quality_score: 0.87
        helpfulness_ratio: 0.91
        published_at: datetime
        author_name: string
        body_preview: string
        reading_time_minutes: 8
        relevance_score: 0.94
        matched_terms: [display, troubleshooting, mri]
    pagination:
      page: 1
      page_size: 20
      total_items: 5
      total_pages: 1
    facets:
      categories:
        TROUBLESHOOTING: 3
        DEVICE_MANUAL: 2
      tags:
        mri: 4
        display: 2
```

---

## 4. REQUEST/RESPONSE DTOs

### 4.1 Common DTOs

```python
# Pagination Request
class PaginationRequest:
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)


# Sort Request
class SortRequest:
    sort: str = Field(default="-created_at")
    # Format: [-]field_name
    # - prefix = descending


# Date Range Filter
class DateRangeFilter:
    date_from: datetime | None = None
    date_to: datetime | None = None


# Standard List Response
class ListResponse[T]:
    data: list[T]
    pagination: PaginationInfo
    meta: dict | None = None


class PaginationInfo:
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


# Error Response
class ErrorResponse:
    error: ErrorDetail


class ErrorDetail:
    code: str  # Machine-readable error code
    message: str  # Human-readable message
    details: list[FieldError] | None = None
    request_id: str | None = None
    correlation_id: str | None = None


class FieldError:
    field: str  # e.g., "priority"
    code: str  # e.g., "INVALID_ENUM"
    message: str
```

### 4.2 Command DTOs

```python
# CreateIncidentCommand
class CreateIncidentCommand:
    title: str = Field(max_length=200)
    description: str = Field(max_length=5000)
    priority: Priority
    safety_level: SafetyLevel
    category: str
    device_id: UUID | None = None
    device_name: str | None = None
    device_location: str | None = None
    patient_impact: str | None = None
    occurred_at: datetime
    detected_at: datetime
    tags: list[str] | None = None
    correlation_id: UUID | None = None


# TriageIncidentCommand
class TriageIncidentCommand:
    priority: Priority
    category: str
    assigned_to: UUID | None = None
    triage_notes: str | None = Field(max_length=2000, default=None)
    auto_open: bool = False


# ResolveIncidentCommand
class ResolveIncidentCommand:
    resolution_type: str
    resolution_summary: str = Field(max_length=500)
    resolution_details: str = Field(max_length=5000)
    actions_taken: list[str] | None = None
    parts_replaced: list[dict] | None = None
    downtime_minutes: int | None = None
    verified: bool = False
```

---

## 5. ERROR HANDLING

### 5.1 Error Codes

```yaml
# HTTP Status Codes
200: OK - Successful GET, PATCH
201: Created - Successful POST
204: No Content - Successful DELETE
400: Bad Request - Validation error
401: Unauthorized - Invalid/missing authentication
403: Forbidden - Valid auth but no permission
404: Not Found - Resource doesn't exist
409: Conflict - Optimistic locking failure
422: Unprocessable Entity - Business rule violation
429: Too Many Requests - Rate limit exceeded
500: Internal Server Error - Unexpected error
503: Service Unavailable - Dependency down

# Application Error Codes
VALIDATION_ERROR: 400
INVALID_ENUM: 400
REQUIRED_FIELD: 400
INVALID_FORMAT: 400
OUT_OF_RANGE: 400

UNAUTHORIZED: 401
TOKEN_EXPIRED: 401
TOKEN_INVALID: 401

FORBIDDEN: 403
PERMISSION_DENIED: 403
TENANT_MISMATCH: 403

NOT_FOUND: 404
INCIDENT_NOT_FOUND: 404
DEVICE_NOT_FOUND: 404

CONFLICT: 409
CONCURRENCY_ERROR: 409
DUPLICATE_ENTITY: 409

INVALID_STATE_TRANSITION: 422
BUSINESS_RULE_VIOLATION: 422

RATE_LIMIT_EXCEEDED: 429

INTERNAL_ERROR: 500
DEPENDENCY_UNAVAILABLE: 503
```

### 5.2 Error Response Examples

```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Cannot resolve incident in REPORTED status. Incident must be TRIAGED or ACTIVE first.",
    "details": [
      {
        "field": "status",
        "code": "INVALID_STATE_TRANSITION",
        "message": "Current status is REPORTED, cannot transition to RESOLVED"
      }
    ],
    "request_id": "req_abc123",
    "correlation_id": "corr_xyz789"
  }
}
```

---

## 6. VERSIONING STRATEGY

### 6.1 API Versioning

```
URL Versioning: /api/v1/, /api/v2/

Header Versioning (optional): Accept: application/vnd.eren.v1+json

Deprecation:
  - Old version runs in parallel for 2 major versions
  - Deprecation header: Deprecation: true
  - Sunset header: Sunset: Sat, 01 Jan 2027 00:00:00 GMT
  - Link header: Link: <https://api.eren.io/api/v2>; rel="successor-version"
```

### 6.2 Breaking vs Non-Breaking Changes

```
BREAKING (require version bump):
  - Remove endpoint
  - Remove required field
  - Add required field
  - Change field type
  - Change field semantics
  - Rename field
  - Change validation rules

NON-BREAKING (no version bump):
  - Add new optional field
  - Add new endpoint
  - Add new enum value (for consumers using strict typing)
  - Expand max length
  - Relax validation
  - Add new query parameter
  - Add new header
```

---

*Documento generado para implementación. Fase 8 completa.*
