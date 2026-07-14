# EREN OS Cognitive Capability SDK

> **Philosophy**: Developers never implement directly the Cognitive Kernel. They develop capabilities using the Capability SDK.

This document describes the Cognitive Capability SDK (CCSDK), the official framework for developing cognitive capabilities for EREN.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Base Capability](#base-capability)
4. [Lifecycle](#lifecycle)
5. [Builder](#builder)
6. [Registry](#registry)
7. [Usage](#usage)
8. [Integration](#integration)
9. [Roadmap](#roadmap)

---

## Overview

The Cognitive Capability SDK provides a stable API for developing cognitive capabilities without depending directly on the Cognitive Kernel.

### Key Principles

1. **Isolation**: Capabilities are independent of the Kernel
2. **Contracts**: All access occurs through contracts
3. **Lifecycle**: Well-defined lifecycle for all capabilities
4. **Observability**: Complete events, metrics, and tracing

### Capability Categories

| Category | Description |
|----------|-------------|
| `REASONING` | Reasoning capabilities |
| `MEMORY` | Memory management |
| `KNOWLEDGE` | Knowledge retrieval |
| `TOOL` | Tool capabilities |
| `LLM` | Language models |
| `DEVICE` | Biomedical devices |
| `CONNECTOR` | External systems |
| `CUSTOM` | Custom capabilities |

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Cognitive Plugin Framework                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Cognitive Capability SDK                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  BaseCapability   │  │  Builder         │  │  Lifecycle      │  │
│  │                  │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Registry        │  │  Context         │  │  Validation     │  │
│  │                  │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Structure

```
core/sdk/
├── __init__.py           # Main exports
├── capability.py         # BaseCapability
├── builder.py            # CapabilityBuilder
├── lifecycle.py          # LifecycleManager
├── registry.py           # CapabilityRegistry
├── types.py              # Types and enums
└── exceptions.py         # All exceptions
```

---

## Base Capability

### Interface

All capabilities must implement:

```python
class MyCapability(BaseCapability):
    def initialize(self, context: CapabilityContext) -> None:
        """Set up the capability."""
        pass

    def execute(self, context: CapabilityContext) -> CapabilityResult:
        """Execute the capability."""
        return CapabilityResult(success=True)

    def shutdown(self) -> None:
        """Clean up resources."""
        pass
```

### Optional Methods

```python
def health(self) -> CapabilityHealth:
    """Return health status."""
    return CapabilityHealth(healthy=True)

def metadata(self) -> CapabilityMetadata:
    """Return capability metadata."""
    return CapabilityMetadata(
        name="MyCapability",
        version="1.0.0",
        category=CapabilityCategory.REASONING,
    )

def validate(self) -> ValidationResult:
    """Validate the capability."""
    return ValidationResult(is_valid=True)
```

---

## Lifecycle

### States

| State | Description |
|-------|-------------|
| `CREATED` | Capability created |
| `VALIDATED` | Validation passed |
| `REGISTERED` | Registered in registry |
| `INITIALIZED` | Initialized |
| `READY` | Ready to execute |
| `EXECUTING` | Currently executing |
| `COMPLETED` | Execution completed |
| `FAILED` | Error occurred |
| `DISPOSED` | Cleaned up |

### Transitions

```
CREATED
   │
   ▼
VALIDATED
   │
   ▼
REGISTERED
   │
   ▼
INITIALIZED
   │
   ▼
READY ◄──────────────────┐
   │                     │
   ▼                     │
EXECUTING               │
   │                     │
   ├──► COMPLETED ───────┘
   │                     │
   └──► FAILED ──────────┘
```

---

## Builder

### Creating Capabilities

```python
from core.sdk import CapabilityBuilder, CapabilityCategory

metadata = (
    CapabilityBuilder()
    .named("OpenAI Reasoning")
    .category(CapabilityCategory.LLM)
    .version("1.0.0")
    .description("OpenAI GPT reasoning capability")
    .implements("ReasoningContract")
    .depends_on("MemoryCapability")
    .configure(api_key="...")
    .build()
)
```

### Creating Capability Classes

```python
from core.sdk import CapabilityClassBuilder

def my_execute(context):
    return CapabilityResult(success=True, data={"result": "ok"})

CapabilityClass = (
    CapabilityClassBuilder()
    .named("MyCapability")
    .version("1.0.0")
    .executes(my_execute)
    .create_class()
)
```

---

## Registry

### Registering Capabilities

```python
from core.sdk import get_capability_registry

registry = get_capability_registry()

# Register capability
registry.register("my-capability", capability)

# List all
capabilities = registry.list_all()

# Get capability
capability = registry.get("my-capability")
```

### Lifecycle Management

```python
from core.sdk import get_lifecycle_manager

lifecycle = get_lifecycle_manager()

# Initialize
lifecycle.initialize(capability, context)

# Execute
result = lifecycle.execute(capability, context)

# Shutdown
lifecycle.shutdown(capability)
```

---

## Usage

### Full Example

```python
from core.sdk import (
    BaseCapability,
    CapabilityBuilder,
    CapabilityContext,
    CapabilityResult,
    CapabilityCategory,
    get_capability_registry,
    get_lifecycle_manager,
)

class MyCapability(BaseCapability):
    def initialize(self, context):
        self.context = context
        print(f"Initialized: {self.capability_id}")

    def execute(self, context):
        return CapabilityResult(
            success=True,
            data={"message": "Hello from capability!"}
        )

    def shutdown(self):
        print(f"Shutdown: {self.capability_id}")

# Create and register
registry = get_capability_registry()
lifecycle = get_lifecycle_manager()

capability = MyCapability()
registry.register("my-capability", capability)

# Execute
context = CapabilityContext(
    capability_id="my-capability",
    execution_id="exec-001",
)

lifecycle.initialize(capability, context)
result = lifecycle.execute(capability, context)
lifecycle.shutdown(capability)

print(result.data)
```

---

## Integration

### With Plugin Framework

Capabilities can be exposed as plugins:

```python
from core.plugins import PluginManifestBuilder, PluginCategory

manifest = (
    PluginManifestBuilder()
    .plugin_id("my-capability")
    .version("1.0.0")
    .category(PluginCategory.COGNITIVE)
    .implements("CapabilityContract")
    .build()
)
```

### With Router

Capabilities can be selected by the router:

```python
from core.router import Router

router = Router()
router.register_route("diagnostic", "my-capability")
selected = router.select("diagnostic")
```

---

## Roadmap

### Phase 1: Core Infrastructure ✓
- [x] BaseCapability
- [x] Builder
- [x] LifecycleManager
- [x] Registry
- [x] Types

### Phase 2: Advanced Features
- [ ] Capability validation framework
- [ ] Capability versioning
- [ ] Capability hot reload
- [ ] Capability sandboxing

### Phase 3: Standard Capabilities
- [ ] OpenAI LLM Capability
- [ ] Claude LLM Capability
- [ ] Memory Capability
- [ ] Knowledge Capability

---

## References

- [Architecture Overview](./architecture-overview.md)
- [Plugin Framework](./plugins.md)
- [Capability Registry](../core/capability-registry.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
