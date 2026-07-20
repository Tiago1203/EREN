# EREN Testing Guide
## Testing Strategy for Epic 1

---

## Overview

Epic 1 uses a **three-layer testing pyramid** with 17 unit tests and 3 integration tests:

```
        /\
       /  \         Integration tests (3)
      /____\        (Real DB, RabbitMQ, Redis)
     /      \
    /________\      Unit tests (17+)
   /          \      (No external dependencies)
```

---

## Running Tests

```bash
cd apps/api

# All tests
uv run pytest tests/ -v

# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# With coverage
uv run pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# Watch mode
uv run pytest tests/ -v --watch

# Specific test file
uv run pytest tests/unit/test_device_service.py -v

# Specific test
uv run pytest tests/unit/test_device_service.py::TestDeviceService::test_get_device_by_id -v
```

---

## Test Structure

```
apps/api/tests/
├── conftest.py              # Shared fixtures
├── __init__.py
├── test_health.py          # Health endpoint tests
├── unit/
│   ├── __init__.py
│   ├── test_device_router.py
│   ├── test_device_service.py
│   ├── test_diagnosis_service.py
│   ├── test_diagnosis_service_negative.py
│   ├── test_patient_service.py
│   ├── test_patient_service_negative.py
│   ├── test_work_order_router.py
│   └── test_work_order_service.py
└── integration/
    ├── __init__.py
    ├── test_clinical_flow.py
    ├── test_device_flow.py
    └── test_patient_flow.py
```

---

## Unit Tests

Unit tests use **synchronous dependency overrides** to avoid async/sync conflicts:

```python
# Sync override to avoid asyncio_mode=auto issues
def override_get_device_repository():
    return MockDeviceRepository()

app.dependency_overrides[get_device_repository] = override_get_device_repository
```

### Example: Device Service Test

```python
class TestDeviceService:
    def test_get_device_by_id(self):
        # Given
        repo = MockDeviceRepository()
        service = DeviceService(repo=repo)
        device_id = DeviceId(value="123")

        # When
        result = service.get_device(device_id)

        # Then
        assert result.is_ok()
        assert result.unwrap().id == device_id

    def test_get_device_not_found(self):
        # Given
        repo = MockDeviceRepository(return_none=True)
        service = DeviceService(repo=repo)

        # When
        result = service.get_device(DeviceId(value="999"))

        # Then
        assert result.is_ok()
        assert result.unwrap() is None
```

---

## Integration Tests

Integration tests require a **live PostgreSQL database**. They are tagged:

```python
import pytest

@pytest.mark.integration
class TestDeviceFlow:
    async def test_device_lifecycle(self, db_session):
        # Full lifecycle: create → get → update → delete
        service = DeviceService(repo=DeviceRepositoryImpl(db_session))

        # Create
        device = create_test_device()
        result = await service.create_device(device)
        assert result.is_ok()

        # Get
        fetched = await service.get_device(device.id)
        assert fetched.unwrap().name == device.name

        # Update
        updated = await service.update_status(device.id, DeviceStatus("in_maintenance"))
        assert updated.unwrap().status == DeviceStatus("in_maintenance")
```

---

## Test Fixtures (conftest.py)

```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_device_repository():
    return MagicMock()

@pytest.fixture
async def db_session():
    # Real async session for integration tests
    from app.core.database import get_session_factory
    factory = get_session_factory()
    async with factory() as session:
        yield session
        await session.rollback()

@pytest.fixture
def test_settings():
    return Settings(database_url="postgresql+asyncpg://eren:eren@localhost:5432/eren_test")
```

---

## Test Naming Convention

| Pattern | Example |
|---------|---------|
| `test_{method}_{scenario}` | `test_get_device_by_id_found` |
| `test_{method}_{scenario}_not_found` | `test_create_device_validation_error` |
| `test_{method}_{scenario}_negative` | `test_update_status_invalid_status` |

---

## Coverage Targets

| Layer | Target | Current |
|-------|--------|---------|
| Infrastructure | > 80% | Baseline |
| Domain services | > 90% | Baseline |
| Routers | > 70% | Baseline |
| **Overall** | **> 75%** | Baseline |

Run coverage:

```bash
uv run pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
open htmlcov/index.html
```

---

## CI Integration

Tests run automatically on every push and PR via `.github/workflows/ci.yml`:

```yaml
test:
  steps:
    - name: Run unit tests
      run: |
        cd apps/api
        PYTHONPATH="$GITHUB_WORKSPACE:$GITHUB_WORKSPACE/apps/api" \
        uv run pytest tests/unit -v --tb=short
      env:
        EREN_API_DATABASE_URL: postgresql+asyncpg://eren:eren@localhost:5432/eren_test
```

---

## Adding New Tests

### 1. Unit test (preferred)

```bash
# File: tests/unit/test_<domain>_service.py
touch tests/unit/test_my_service.py
```

### 2. Integration test

```bash
# File: tests/integration/test_<domain>_flow.py
touch tests/integration/test_my_flow.py
```

### 3. Register marker in pytest.ini

```ini
[pytest]
markers =
    unit: Unit tests using sync dependency overrides
    integration: Integration tests requiring real database
```

---

## Mocking Guidelines

| Use case | Tool |
|----------|------|
| Repositories | `unittest.mock.MagicMock` |
| External APIs | `responses` or `httpx` |
| Database | Real DB (integration) or `MagicMock` (unit) |
| RabbitMQ | `aio_pika` mock |
| Redis | `fakeredis` |

---

*EREN Testing Guide v1.0*
*Infrastructure Team - 2026-07-16*
