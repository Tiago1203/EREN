# EREN - Especificación Técnica Completa
## Fase 11: Testing

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  

---

## 1. TEST PYRAMID

```
                    ┌─────────────┐
                    │    E2E     │  50 tests
                    │   Tests    │
              ┌─────┴─────────────┴─────┐
              │    Contract Tests       │  100 tests
              │    (Pact Broker)       │
        ┌─────┴───────────────────────┴─────┐
        │     Integration Tests             │  200 tests
        │     (Testcontainers)              │
  ┌─────┴─────────────────────────────────┴─────┐
  │           Unit Tests                         │  1000 tests
  │           (pytest)                          │
  └─────────────────────────────────────────────┘

Target Coverage:
  - Unit tests: 90%+ line coverage
  - Integration: Critical paths
  - Contract: All API boundaries
  - E2E: Critical user journeys
```

---

## 2. UNIT TESTS

### 2.1 Structure

```python
# Pattern: Given-When-Then
class TestEngineeringIncident:
    """Unit tests for EngineeringIncident aggregate."""
    
    def test_create_incident_generates_event(self):
        # Given
        tenant_id = TenantId.generate()
        
        # When
        incident = EngineeringIncident.create(
            tenant_id=tenant_id,
            title="MRI display flickering",
            description="...",
            priority=Priority.high(),
            safety_level=SafetyLevel.class_c(),
            category=IncidentCategory.HARDWARE_FAILURE,
            reported_by=EngineerId.generate(),
            occurred_at=datetime.now(UTC),
            detected_at=datetime.now(UTC),
        )
        
        # Then
        events = incident.pop_pending_events()
        assert len(events) == 1
        assert isinstance(events[0], IncidentReportedEvent)
        assert events[0].tenant_id == tenant_id
        assert events[0].priority == Priority.high()
    
    def test_invalid_transition_raises_error(self):
        # Given
        incident = self._create_resolved_incident()
        
        # When/Then
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            incident.triage(...)
        
        assert "REPORTED" in str(exc_info.value)
        assert "TRIAGED" in str(exc_info.value)
```

### 2.2 Test Data Builders

```python
class IncidentBuilder:
    """Builder for test incidents."""
    
    def __init__(self):
        self._tenant_id = TenantId.generate()
        self._title = "Test Incident"
        self._priority = Priority.medium()
        self._status = IncidentStatus.REPORTED
    
    def with_priority(self, priority: Priority) -> IncidentBuilder:
        self._priority = priority
        return self
    
    def with_status(self, status: IncidentStatus) -> IncidentBuilder:
        self._status = status
        return self
    
    def build(self) -> EngineeringIncident:
        return EngineeringIncident.create(
            tenant_id=self._tenant_id,
            title=self._title,
            description="Test description",
            priority=self._priority,
            status=self._status,
            ...
        )

# Usage
incident = (
    IncidentBuilder()
    .with_priority(Priority.critical())
    .with_status(IncidentStatus.ACTIVE)
    .build()
)
```

### 2.3 Domain Test Coverage Requirements

```
Incident Aggregate:
  - All state transitions (valid and invalid)
  - All invariants (business rules)
  - Event generation
  - Version incrementing
  - Optimistic locking
  
Recommendation Aggregate:
  - Confidence calculation
  - State transitions
  - Explanation generation
  - Safety classification

Device Aggregate:
  - Lifecycle transitions
  - Calibration tracking
  - Location changes
  - Maintenance scheduling

KnowledgeArticle Aggregate:
  - Review workflow
  - Publication process
  - Cross-references
```

---

## 3. INTEGRATION TESTS

### 3.1 Testcontainers

```python
@pytest.fixture(scope="module")
def postgres_container():
    """PostgreSQL testcontainer."""
    container = PostgreSQLContainer("postgres:16-alpine")
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="module")
def rabbitmq_container():
    """RabbitMQ testcontainer."""
    container = RabbitMQContainer("rabbitmq:3.12-management-alpine")
    container.start()
    yield container
    container.stop()


@pytest.fixture
async def db_pool(postgres_container):
    """Async database pool."""
    pool = await asyncpg.create_pool(
        host=postgres_container.host,
        port=postgres_container.port,
        database=postgres_container.dbname,
        user=postgres_container.username,
        password=postgres_container.password,
    )
    yield pool
    await pool.close()


class TestIncidentRepository:
    """Integration tests for IncidentRepository."""
    
    async def test_save_and_retrieve(self, db_pool):
        # Given
        repo = PostgresIncidentRepository(db_pool)
        incident = IncidentBuilder().build()
        
        # When
        await repo.save(incident)
        retrieved = await repo.get_by_id(incident.id, incident.tenant_id)
        
        # Then
        assert retrieved.is_ok()
        assert retrieved.unwrap().id == incident.id
        assert retrieved.unwrap().title == incident.title
    
    async def test_optimistic_locking(self, db_pool):
        # Given
        repo = PostgresIncidentRepository(db_pool)
        incident = IncidentBuilder().build()
        await repo.save(incident)
        
        # When - concurrent update
        incident_v1 = await repo.get_by_id(incident.id)
        incident_v2 = await repo.get_by_id(incident.id)
        
        incident_v1.triage(...)
        await repo.save(incident_v1)
        
        incident_v2.triage(...)
        result = await repo.save(incident_v2)
        
        # Then
        assert result.is_err()
        assert isinstance(result.unwrap_err(), ConcurrencyError)
```

---

## 4. CONTRACT TESTS

### 4.1 Pact Specification

```python
# Provider: Incident Service
# Consumer: Recommendation Service

# incident_service.pact.py

@pytest.fixture
def incident_service():
    return Pact(
        "recommendation-service",
        "incident-service",
        port=8001,
        pact_dir="./pacts"
    )

@incident_service.parametrize(
    state="an incident with ID inc-123 exists",
    provider_states=[
        {"id": "inc-123", "status": "ACTIVE", "priority": "P2_HIGH"}
    ]
)
def test_get_incident(incident_service):
    (
        incident_service
        .given("an incident with ID inc-123 exists")
        .upon_receiving("a request for incident details")
        .with_request(
            method="GET",
            path="/api/v1/internal/incidents/inc-123",
            headers={"X-Tenant-ID": "tenant-123"}
        )
        .will_respond_with(
            status=200,
            headers={"Content-Type": "application/json"},
            body={
                "incident_id": "inc-123",
                "status": "ACTIVE",
                "priority": "P2_HIGH",
                "category": "HARDWARE_FAILURE",
                "device_id": "dev-456"
            }
        )
    )
```

---

## 5. E2E TESTS

### 5.1 Critical User Journeys

```python
# E2E: Create and resolve incident

@pytest.fixture
def browser():
    return PlaywrightBrowser()


def test_create_and_resolve_incident(browser):
    # Login
    browser.goto("/login")
    browser.fill("[name=email]", "engineer@hospital.com")
    browser.fill("[name=password]", "password")
    browser.click("[type=submit]")
    
    assert browser.url.endswith("/dashboard")
    
    # Create incident
    browser.goto("/incidents/new")
    browser.fill("[name=title]", "MRI Scanner Error")
    browser.select_option("[name=priority]", "P2_HIGH")
    browser.select_option("[name=category]", "HARDWARE_FAILURE")
    browser.click("button[type=submit]")
    
    # Verify redirect
    assert "inc-" in browser.url
    
    # Verify incident appears
    browser.goto("/incidents")
    assert "MRI Scanner Error" in browser.text_content()
    
    # Triage
    browser.click("[data-testid=incident-row]")
    browser.click("button:Triage")
    browser.select_option("[name=priority]", "P1_CRITICAL")
    browser.click("button:Confirm")
    
    # Resolve
    browser.click("button:Resolve")
    browser.fill("[name=resolution_summary]", "Replaced faulty cable")
    browser.click("button:Submit Resolution")
    
    # Verify status
    assert "RESOLVED" in browser.text_content()
```

---

*Documento generado para implementación. Fase 11 completa.*
