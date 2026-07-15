# ADR-0001: EREN Adopts Hexagonal Architecture

## Status
**Status:** Accepted  
**Date:** 2026-07-15  
**Deciders:** Architecture Board

---

## Context

EREN is a cognitive operating system for hospitals. It must:
- Support multiple LLM providers (OpenAI, Anthropic, etc.)
- Integrate with clinical systems (FHIR, HL7, DICOM)
- Operate securely under HIPAA
- Evolve over decades without rewriting

We need an architecture that:
- Decouples core business logic from infrastructure
- Enables swapping implementations without code changes
- Supports dependency injection for testability
- Scales from prototype to production

---

## Decision

EREN adopts **Hexagonal Architecture** (also known as Ports and Adapters).

```
┌─────────────────────────────────────────────────────────────────┐
│                         APPLICATION                              │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    CORE / DOMAIN                        │   │
│   │                                                          │   │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐        │   │
│   │   │Cognitive │   │ Security │   │Clinical  │        │   │
│   │   │Domain    │   │ Domain   │   │ Domain   │        │   │
│   │   └──────────┘   └──────────┘   └──────────┘        │   │
│   │                                                          │   │
│   │   ┌──────────────────────────────────────────────┐     │   │
│   │   │              CONTRACTS (Ports)               │     │   │
│   │   │  IdentityProvider  TrustProvider  etc.      │     │   │
│   │   └──────────────────────────────────────────────┘     │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ▼                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 ADAPTERS (Implementations)               │   │
│   │                                                          │   │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│   │   │ Supabase │  │  OpenAI  │  │   FHIR   │            │   │
│   │   │   Auth   │  │ Provider │  │ Adapter  │            │   │
│   │   └──────────┘  └──────────┘  └──────────┘            │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Consequences

### Positive

1. **Testability**: Core logic can be tested with mock adapters
2. **Flexibility**: Swap implementations without changing core
3. **Evolution**: Add new providers without modifying existing code
4. **Clarity**: Clear boundaries between what and how

### Negative

1. **Complexity**: More layers than simple architecture
2. **Indirection**: More files, more interfaces
3. **Learning curve**: Team must understand hexagonal patterns

### Risks

- Contract drift (implementation diverging from contract)
- Over-engineering for simple features
- Too many abstractions

---

## Implementation

### Directory Structure

```
eren/
├── core/
│   ├── contracts/           # Ports (interfaces)
│   │   ├── cognitive/
│   │   │   ├── trust.py     # TrustProvider contract
│   │   │   └── ...
│   │   ├── security/
│   │   │   ├── identity.py  # IdentityProvider contract
│   │   │   └── ...
│   │   └── ...
│   │
│   ├── capabilities/         # Core logic
│   │   ├── cognitive/
│   │   │   └── trust/       # Trust implementation
│   │   │       ├── provider.py
│   │   │       └── ...
│   │   └── ...
│   │
│   └── adapters/            # Implementations
│       ├── supabase/
│       │   └── identity.py   # Supabase implementation
│       ├── openai/
│       │   └── provider.py   # OpenAI implementation
│       └── ...
```

### Contract Pattern

```python
# core/contracts/security/identity.py
class IdentityProvider(Protocol):
    """Port: Authentication services."""
    
    async def authenticate(self, credentials: dict) -> AuthenticationResult: ...

# core/adapters/supabase/identity.py
class SupabaseIdentityProvider:
    """Adapter: Supabase implementation."""
    
    async def authenticate(self, credentials: dict) -> AuthenticationResult:
        # Supabase-specific implementation
        ...

# core/capabilities/security/identity/provider.py
class DefaultIdentityProvider(IdentityProvider):
    """Default implementation."""
    
    def __init__(self, adapter: IdentityProvider):
        self._adapter = adapter
    
    async def authenticate(self, credentials: dict) -> AuthenticationResult:
        return await self._adapter.authenticate(credentials)
```

---

## Alternatives Considered

### 1. Layered Architecture
- Simpler to understand
- Less indirection
- But: Dependencies flow in wrong direction (infra → domain)

### 2. Microservices
- Independent deployment
- But: Complexity of distributed systems
- Overkill for EREN's current scale

### 3. Modular Monolith
- Simpler deployment
- But: Harder to test individual modules
- Not enough isolation

---

## References

- [Ports and Adapters by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture in Python](https://python-patterns.guide/python/hexagonal-architecture/)

---

## Review History

| Date | Reviewer | Notes |
|------|----------|-------|
| 2026-07-15 | Architecture Board | Initial acceptance |
