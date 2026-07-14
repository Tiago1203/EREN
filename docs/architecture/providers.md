# Cognitive Multi-Provider Layer (CMPL)

> **Philosophy**: The Cognitive Kernel never knows a specific provider. All cognitive capabilities use a common provider contract.

This document describes the Multi-Provider Layer, the official abstraction layer for LLM providers in EREN OS.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Provider Contract](#provider-contract)
4. [Selection Policies](#selection-policies)
5. [Configuration](#configuration)
6. [Integration](#integration)
7. [Events](#events)
8. [Metrics](#metrics)
9. [Health Checks](#health-checks)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Multi-Provider Layer provides a unified interface for using multiple LLM providers with automatic selection, failover, and load balancing.

### Key Features

- **Provider Abstraction**: Single interface for all LLM providers
- **Automatic Selection**: Multiple selection strategies
- **Failover**: Automatic fallback on provider failure
- **Load Balancing**: Round-robin and priority-based balancing
- **Health Monitoring**: Real-time provider health checks
- **Metrics**: Request tracking and cost analysis

### Supported Providers

| Provider | Type | Local | Cloud |
|----------|------|-------|-------|
| OpenAI | `openai` | ❌ | ✅ |
| Claude | `claude` | ❌ | ✅ |
| Ollama | `ollama` | ✅ | ❌ |
| Gemini | `gemini` | ❌ | ✅ |
| Azure OpenAI | `azure_openai` | ❌ | ✅ |

---

## Architecture

### Module Structure

```
core/providers/
├── __init__.py           # Exports
├── provider.py           # BaseProvider contract
├── registry.py          # ProviderRegistry
├── selector.py          # ProviderSelector
├── manager.py           # ProviderManager
├── types.py             # Types and enums
├── exceptions.py        # Exception types
└── README.md            # Quick start
```

### Components

| Component | Description |
|-----------|-------------|
| `BaseProvider` | Abstract base for all providers |
| `ProviderRegistry` | Manages provider registration |
| `ProviderSelector` | Implements selection strategies |
| `ProviderManager` | Orchestrates all operations |

### Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Cognitive Runtime                             │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                 Execution Coordinator
                              │
                              ▼
                    Reasoning Pipeline
                              │
                              ▼
                 Multi Provider Layer
        ┌────────────┬─────────────┬─────────────┬─────────────┐
        ▼            ▼             ▼             ▼
    OpenAI      Claude        Ollama       Gemini
                              │
                              ▼
                 Provider Manager
                              │
                              ▼
                 Provider Selector
                              │
                              ▼
                   Selected Provider
                              │
                              ▼
                    GenerationResponse
```

---

## Provider Contract

All providers must implement `BaseProvider`:

```python
class BaseProvider(ABC):
    @property
    def provider_id(self) -> str: ...

    @property
    def provider_type(self) -> ProviderType: ...

    @property
    def state(self) -> ProviderState: ...

    @property
    def metrics(self) -> ProviderMetrics: ...

    def initialize(self, config: ProviderConfig) -> None: ...

    def generate(self, request: GenerationRequest) -> GenerationResponse: ...

    def shutdown(self) -> None: ...

    # Optional
    def stream(self, request: GenerationRequest) -> AsyncIterator[str]: ...

    def embeddings(self, texts: list[str], model: str = "") -> list[list[float]]: ...

    def health_check(self) -> ProviderHealth: ...
```

### Lifecycle

```
UNREGISTERED → REGISTERED → INITIALIZED → HEALTHY → UNHEALTHY
                    │            │           │           │
                    └────────────┴───────────┴───────────┘
                                    │
                              Can also be:
                              DEGRADED | DISABLED | UNAVAILABLE
```

---

## Selection Policies

| Policy | Description | Use Case |
|--------|-------------|----------|
| `DEFAULT` | Uses default provider | Simple deployments |
| `PRIORITY` | Highest priority healthy | Production with primary/secondary |
| `ROUND_ROBIN` | Balanced distribution | Load balancing |
| `HEALTHY_FIRST` | Only healthy providers | High availability |
| `LOWEST_LATENCY` | Fastest response time | Performance optimization |
| `FAILOVER` | Automatic fallback | Reliability |
| `RANDOM` | Random selection | Testing |

### Usage Examples

```python
# Default selection
response = manager.generate(request)

# Priority-based
response = manager.generate(request, policy=SelectionPolicy.PRIORITY)

# With failover
response = manager.generate(
    request,
    policy=SelectionPolicy.FAILOVER,
    fallback_enabled=True
)
```

---

## Configuration

### Basic Configuration

```python
from core.providers import ProviderConfig, ProviderType

config = ProviderConfig(
    provider_id="openai-primary",
    provider_type=ProviderType.OPENAI,
    enabled=True,
    priority=1,
    endpoint="https://api.openai.com/v1",
    api_key="sk-...",
    timeout=60,
    max_retries=3,
    default_model="gpt-5-mini",
    models=["gpt-5", "gpt-4", "gpt-4o"],
)
```

### Multi-Provider Setup

```python
from core.providers import ProviderManager, ProviderConfig, ProviderType

manager = ProviderManager(
    default_policy=SelectionPolicy.PRIORITY,
    default_provider_id="openai-primary",
)

# Add providers
manager.add_provider(
    OpenAIProvider(),
    ProviderConfig(
        provider_id="openai-primary",
        provider_type=ProviderType.OPENAI,
        enabled=True,
        priority=1,
        models=["gpt-5", "gpt-4"],
    )
)

manager.add_provider(
    OllamaProvider(),
    ProviderConfig(
        provider_id="ollama-local",
        provider_type=ProviderType.OLLAMA,
        enabled=True,
        priority=2,
        endpoint="http://localhost:11434",
        models=["llama3", "mistral"],
    )
)
```

---

## Integration

### With Runtime

```python
from core.runtime import CognitiveRuntime
from core.providers import ProviderManager, ProviderConfig, ProviderType

# Create runtime
runtime = CognitiveRuntime()

# Configure providers
manager = runtime.providers
manager.add_provider(OpenAIProvider(), config)
manager.add_provider(OllamaProvider(), config)

# Runtime automatically uses provider layer
result = await runtime.execute(task)
```

### With Capability SDK

```python
from core.sdk import CapabilityContext
from core.providers import ProviderManager

manager = ProviderManager()
manager.add_provider(OpenAIProvider(), config)

# Use in capability
context = CapabilityContext(
    capability_id="reasoning",
    metadata={"provider": "openai"},
)

result = capability.execute(context)
```

### With Diagnostics

```python
from core.diagnostics import ERENDiagnostics

# Include provider checks in diagnostics
report = ERENDiagnostics().run_full_system_validation()

# Check provider health
provider_health = report.section("providers")
print(f"Score: {provider_health.score}%")
```

---

## Events

| Event | Description |
|-------|-------------|
| `ProviderSelected` | Provider selected for request |
| `ProviderChanged` | Provider changed (failover) |
| `ProviderUnavailable` | Provider became unavailable |
| `ProviderRecovered` | Provider recovered |
| `ProviderRequestStarted` | Request started |
| `ProviderRequestCompleted` | Request completed |
| `ProviderRequestFailed` | Request failed |

### Event Handling

```python
manager.on("ProviderSelected", lambda data: print(f"Selected: {data['provider_id']}"))
manager.on("ProviderUnavailable", handle_failover)
```

---

## Metrics

### Tracked Metrics

- `total_requests`: Total requests
- `successful_requests`: Successful requests
- `failed_requests`: Failed requests
- `success_rate`: Success percentage
- `total_input_tokens`: Input tokens
- `total_output_tokens`: Output tokens
- `average_latency_ms`: Average latency
- `total_cost`: Estimated cost
- `retry_count`: Number of retries
- `failover_count`: Number of failovers

### Usage

```python
metrics = provider.metrics.to_dict()

print(f"Success rate: {metrics['success_rate']:.1f}%")
print(f"Average latency: {metrics['average_latency_ms']:.0f}ms")
print(f"Total cost: ${metrics['total_cost']:.4f}")
```

---

## Health Checks

### Health Status

| Status | Condition |
|--------|-----------|
| `HEALTHY` | Provider operational |
| `DEGRADED` | Limited functionality |
| `UNHEALTHY` | Not operational |

### Check Implementation

```python
# Check single provider
health = manager.health_check("openai-primary")
print(f"Status: {health.state}")
print(f"Latency: {health.latency_ms}ms")

# Check all providers
all_health = manager.health_check_all()
for provider_id, health in all_health.items():
    print(f"{provider_id}: {health.state}")
```

---

## Troubleshooting

### Common Issues

#### Provider Not Found
```
ProviderNotFoundError: Provider not found: openai-primary
```
**Solution**: Verify provider is registered and enabled.

#### All Providers Failed
```
ProviderFallbackError: All providers failed
```
**Solution**: Check provider configurations and network connectivity.

#### Rate Limit Exceeded
```
ProviderRateLimitError: Rate limit exceeded
```
**Solution**: Implement exponential backoff or reduce request frequency.

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug for providers
logger = logging.getLogger("core.providers")
logger.setLevel(logging.DEBUG)
```

---

## References

- [Runtime Architecture](./runtime.md)
- [Capability SDK](./capability-sdk.md)
- [Plugin Framework](./plugins.md)
- [Diagnostics](./production-readiness.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
