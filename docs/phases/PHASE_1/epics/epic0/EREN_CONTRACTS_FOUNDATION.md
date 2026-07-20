# EREN Contracts Foundation
## Phase 4: Contract Templates

---

## Overview

This document establishes the contract foundation for EREN's capabilities. Contracts define the interfaces that capabilities must implement, ensuring:
- **Decoupling**: Capabilities can be swapped without affecting others
- **Testability**: Contracts enable mocking and testing
- **Evolution**: New implementations can be added without breaking existing code
- **Clarity**: Public interfaces are clearly defined

---

## Contract Structure

Each capability follows a consistent contract structure:

```
core/contracts/
├── <domain>/
│   ├── __init__.py
│   ├── provider.py          # Main Protocol
│   ├── types.py             # Data classes
│   ├── events.py            # Domain events
│   └── exceptions.py        # Specific exceptions
```

---

## Foundation Contracts

### Security Contracts

#### 1. Identity Contract
**File:** `core/contracts/security/identity.py`

```python
class IdentityProvider(Protocol):
    """Manages authentication and identity."""
    
    async def authenticate(credentials: dict) -> AuthenticationResult
    async def verify_token(token: str) -> Principal | None
    async def get_principal(principal_id: str) -> Principal | None
    async def create_session(principal: Principal) -> Session
    async def invalidate_session(session_id: str) -> bool
```

**Key Types:**
- `Principal`: Authenticated identity
- `Session`: Active session
- `IdentityType`: HUMAN, DEVICE, SYSTEM, SERVICE

#### 2. Authorization Contract
**File:** `core/contracts/security/authorization.py`

```python
class AuthorizationProvider(Protocol):
    """Manages access control."""
    
    async def can_perform(request: AuthorizationRequest) -> AuthorizationDecision
    async def get_role(role_id: str) -> Role | None
    async def get_principal_roles(principal_id: str) -> tuple[Role, ...]
    async def assign_role(principal_id: str, role_id: str) -> bool
    async def create_policy(name: str, rules: list[PolicyRule]) -> Policy
```

**Key Types:**
- `AuthorizationRequest`: Who wants to do what
- `AuthorizationDecision`: ALLOW or DENY
- `Role`: Collection of permissions
- `Policy`: Rules for access decisions

#### 3. Audit Contract
**File:** `core/contracts/security/audit.py`

```python
class AuditProvider(Protocol):
    """Immutable audit logging."""
    
    async def log(event: AuditEvent) -> str
    async def log_phi_access(...) -> str  # HIPAA required
    async def log_clinical_decision(...) -> str  # CDS audit
    async def query(query: AuditQuery) -> AuditQueryResult
    async def generate_hipaa_report(...) -> HIPAAComplianceReport
```

**Key Types:**
- `AuditEvent`: Immutable audit record
- `AuditCategory`: AUTHENTICATION, DATA_ACCESS, CLINICAL, etc.
- `PHIExposure`: NONE, MINIMAL, MODERATE, FULL

---

### Cognitive Contracts

#### 4. Trust Contract
**File:** `core/contracts/cognitive/trust.py`

```python
class TrustProvider(Protocol):
    """Evaluates trust in sources and evidence."""
    
    async def evaluate_source_trust(source_id, context) -> TrustScore
    async def evaluate_evidence_trust(evidence_id, context) -> TrustScore
    async def evaluate_device_trust(device_id, calibration) -> TrustScore
    async def get_trust_context(source_id) -> TrustContext | None
    async def reconcile_conflicts(evidence_ids) -> tuple[str, list[str]]
```

**Key Types:**
- `TrustScore`: Level (HIGH/MODERATE/LOW/UNCERTAIN) + score (0.0-1.0)
- `TrustContext`: Factors for evaluation
- `TrustLevel`: Enumeration of trust levels

---

## Contract Templates

### Template: Provider Contract

```python
"""
[Capability] Contract.

Philosophy: [How this capability aligns with EREN philosophy]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Types
# =============================================================================


class [TypeName]Type(Enum):
    """Types of [entity]."""
    TYPE_A = "type_a"
    TYPE_B = "type_b"


@dataclass(frozen=True)
class [Entity]:
    """[Description]"""
    
    entity_id: str
    name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class [ResultType]:
    """Result of [operation]."""
    
    success: bool
    entity: [Entity] | None = None
    error: str | None = None


# =============================================================================
# Provider Interface
# =============================================================================


class [Capability]Provider(Protocol):
    """Contract for [capability] services.
    
    Philosophy: [Key philosophical alignment]
    
    This contract defines the interface that all [capability] 
    implementations must follow.
    """
    
    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...
    
    async def [operation](
        self,
        param: str,
    ) -> [ResultType]:
        """[Operation description].
        
        Args:
            param: [Parameter description]
            
        Returns:
            [ResultType] with outcome
        """
        ...
    
    async def [another_operation](
        self,
        entity_id: str,
    ) -> [Entity] | None:
        """[Operation description].
        
        Args:
            entity_id: [Description]
            
        Returns:
            [Entity] if found, None otherwise
        """
        ...


# =============================================================================
# Events
# =============================================================================


@dataclass(frozen=True)
class [EventName]Event:
    """Fired when [something happens]."""
    
    event_id: str
    entity_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
```

---

## Domain Events

### Security Events

```python
# All security capabilities must publish these events:

AuthenticationSucceeded(principal_id, session_id, method)
AuthenticationFailed(principal_id, error_code, ip_address)
AuthorizationGranted(principal_id, action, resource)
AuthorizationDenied(principal_id, action, resource, reason)
AuditEventLogged(event_id, category, has_phi)
HIPAAAlert(alert_id, indicator_type, severity)
```

### Cognitive Events

```python
TrustEvaluated(source_id, trust_score, method)
TrustUpdated(source_id, previous_score, new_score)
TrustConflictDetected(source_id, conflicting_sources)
```

---

## Exception Hierarchy

```python
class ERENContractError(Exception):
    """Base exception for contract errors."""
    pass


# Security exceptions
class IdentityError(ERENContractError):
    pass

class AuthenticationError(IdentityError):
    pass

class AuthorizationError(ERENContractError):
    pass


# Cognitive exceptions
class TrustError(ERENContractError):
    pass

class EvidenceError(ERENContractError):
    pass
```

---

## Contract Compliance

### Compliance Checklist

For each capability, verify:

```
□ Provider interface defines all required methods
□ All types are frozen dataclasses
□ All methods are async
□ Return types are Optional or typed
□ Events are defined for all significant actions
□ Exceptions are defined
□ Docstrings explain purpose and alignment with philosophy
□ Examples are provided
```

---

## Implementation Guide

### Step 1: Define the Contract

```python
# core/contracts/<domain>/<capability>.py
class CapabilityProvider(Protocol):
    async def operation(param: str) -> Result: ...
```

### Step 2: Implement the Contract

```python
# core/capabilities/<domain>/<capability>/implementations/default.py
class DefaultCapabilityProvider:
    async def operation(self, param: str) -> Result:
        # Implementation
        return Result(success=True, ...)
```

### Step 3: Register the Implementation

```python
# core/capabilities/<domain>/<capability>/__init__.py
from core.contracts.<domain>.<capability> import CapabilityProvider

# Default implementation
provider: CapabilityProvider = DefaultCapabilityProvider()
```

### Step 4: Use in Runtime

```python
# Runtime only knows about the contract
from core.contracts.<domain>.<capability> import CapabilityProvider

class CognitiveRuntime:
    def __init__(self, capability: CapabilityProvider):
        self._capability = capability
```

---

## Priority Contracts to Implement

### Phase 1: Foundation (Must Have)

1. **IdentityProvider** - Authentication
2. **AuthorizationProvider** - Access control
3. **AuditProvider** - Audit logging

### Phase 2: Core Cognitive

4. **TrustProvider** - Trust evaluation
5. **RiskProvider** - Risk assessment
6. **ReasoningProvider** - Reasoning engine

### Phase 3: Clinical

7. **ClinicalContextProvider** - Patient context
8. **DecisionSupportProvider** - CDS
9. **EvidenceProvider** - Evidence retrieval

### Phase 4: Biomedical

10. **DeviceRegistryProvider** - Device tracking
11. **AlarmProvider** - Alarm management
12. **CalibrationProvider** - Calibration tracking

---

## Testing Contracts

### Contract Test Template

```python
import pytest
from core.contracts.security.identity import (
    IdentityProvider,
    Principal,
    AuthenticationResult,
)

class TestIdentityContract:
    """Tests that verify contract compliance."""
    
    @pytest.fixture
    def provider(self) -> IdentityProvider:
        """Override with actual implementation."""
        raise NotImplementedError
    
    async def test_authenticate_returns_principal_on_success(
        self, provider
    ):
        """Authentication must return principal on success."""
        result = await provider.authenticate({
            "email": "test@example.com",
            "password": "valid_password"
        })
        
        assert result.success
        assert result.principal is not None
        assert isinstance(result.principal, Principal)
    
    async def test_authenticate_returns_error_on_failure(
        self, provider
    ):
        """Authentication must return error on failure."""
        result = await provider.authenticate({
            "email": "test@example.com",
            "password": "wrong_password"
        })
        
        assert not result.success
        assert result.error_code is not None
```

---

## Contract Evolution

### Adding Methods to Contracts

When adding new methods to existing contracts:

1. Add method to Protocol
2. Add default implementation (can raise NotImplementedError)
3. Update all implementations
4. Update tests
5. Version the contract

### Breaking Changes

Breaking changes require:
1. New major version of contract
2. Migration path
3. Deprecation period
4. Version documentation

---

*EREN Contracts Foundation v1.0*
*Architecture Board - 2026-07-15*
