# OpenAI Cognitive Capability Plugin

> **Philosophy**: The Cognitive Kernel does not know OpenAI. OpenAI is only a cognitive capability registered as a Plugin.

This document describes the OpenAI Cognitive Capability Plugin (OCP), the first real cognitive capability for EREN.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Capabilities](#capabilities)
4. [Configuration](#configuration)
5. [Supported Models](#supported-models)
6. [Integration](#integration)
7. [Events](#events)
8. [Metrics](#metrics)
9. [Health Checks](#health-checks)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The OpenAI Plugin provides GPT-based reasoning capability for EREN through the Cognitive Plugin Framework and Capability SDK.

### Key Features

- **ReasoningContract**: Implements standard reasoning interface
- **Plugin Framework**: Fully integrated with plugin discovery and lifecycle
- **Capability SDK**: Built using official SDK patterns
- **Multiple Models**: Supports GPT-5, GPT-4, and variants
- **Full Observability**: Events, metrics, and tracing

### System Integration

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Cognitive Runtime                            │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                 Execution Coordinator
                              │
                              ▼
                  Capability Router
                              │
                              ▼
                 Reasoning Pipeline
                              │
                              ▼
              OpenAI Capability Plugin
                              │
                              ▼
                    OpenAI Responses API
                              │
                              ▼
                     GPT Response
```

---

## Architecture

### Module Structure

```
plugins/openai/
├── __init__.py           # Exports
├── plugin.py             # Plugin integration
├── capability.py         # Main capability
├── provider.py           # API client
├── configuration.py      # Config handling
├── models.py             # Model definitions
├── mapper.py             # Request mapping
├── response_mapper.py    # Response mapping
├── exceptions.py         # Error types
├── manifest.yaml         # Plugin manifest
└── README.md             # Quick start
```

### Components

| Component | Description |
|-----------|-------------|
| `OpenAIPlugin` | Plugin descriptor for Framework |
| `OpenAICapability` | Main capability implementation |
| `OpenAIClient` | HTTP client for API |
| `RequestMapper` | Context → OpenAI mapping |
| `ResponseMapper` | OpenAI → EREN mapping |

---

## Capabilities

### ReasoningContract

The plugin implements `ReasoningContract`:

```python
class OpenAICapability(BaseCapability):
    def initialize(self, context: CapabilityContext) -> None
    def execute(self, context: CapabilityContext) -> CapabilityResult
    def shutdown(self) -> None
    def health(self) -> CapabilityHealth
    def metadata(self) -> CapabilityMetadata
```

### Lifecycle

```
DISCOVERED → LOADED → INITIALIZED → ACTIVE → PAUSED
```

---

## Configuration

### Basic Configuration

```python
from plugins.openai import OpenAICapability, OpenAIConfiguration

config = OpenAIConfiguration(
    model="gpt-5-mini",
    temperature=0.2,
    max_tokens=4000,
    timeout=60,
    retries=3,
)

capability = OpenAICapability(
    api_key="sk-your-api-key",
    config=config,
)
```

### Environment Variables

```bash
export OPENAI_API_KEY="sk-your-api-key"
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model` | `gpt-5-mini` | Model identifier |
| `temperature` | `0.2` | Response randomness (0-2) |
| `max_tokens` | `4000` | Max response tokens |
| `timeout` | `60` | Request timeout (seconds) |
| `retries` | `3` | Retry attempts |
| `stream` | `false` | Enable streaming |

---

## Supported Models

| Model | Context | Max Output | Vision | Functions |
|-------|---------|------------|--------|-----------|
| `gpt-5` | 128K | 16K | ✅ | ✅ |
| `gpt-5-mini` | 64K | 8K | ✅ | ✅ |
| `gpt-5-nano` | 32K | 4K | ❌ | ✅ |
| `gpt-4` | 128K | 8K | ❌ | ✅ |
| `gpt-4-turbo` | 128K | 16K | ✅ | ✅ |
| `gpt-4o` | 128K | 16K | ✅ | ✅ |
| `gpt-4o-mini` | 128K | 8K | ✅ | ✅ |

---

## Integration

### With Plugin Framework

```python
from core.plugins import PluginManager
from plugins.openai import create_openai_plugin

manager = PluginManager()
plugin = create_openai_plugin(api_key="sk-...")

# Register and activate
descriptor = manager.discover(plugin.get_manifest())
manager.register(descriptor)
manager.activate("openai-reasoning")
```

### With Capability SDK

```python
from core.sdk import CapabilityContext

context = CapabilityContext(
    capability_id="openai-reasoning",
    execution_id="exec-001",
)

# Initialize and execute
capability.initialize(context)
result = capability.execute(context)
```

### With Router

```python
from core.router import CapabilityRouter

router = CapabilityRouter()
router.register_route("reasoning", "openai-reasoning")

# Route selection
selected = router.select("reasoning")
```

### Full Example

```python
from plugins.openai import OpenAICapability
from core.sdk import CapabilityContext

# Create and initialize
capability = OpenAICapability(api_key="sk-...")
capability.initialize(CapabilityContext())

# Execute reasoning
result = capability.execute(
    CapabilityContext(metadata={
        "prompt": "Explain quantum entanglement",
        "system_prompt": "You are a physicist.",
    })
)

print(result.data["content"])
```

---

## Events

The plugin publishes:

| Event | Description |
|-------|-------------|
| `OpenAIRequestStarted` | Request initiated |
| `OpenAIRequestCompleted` | Request successful |
| `OpenAIRequestFailed` | Request failed |
| `OpenAIModelLoaded` | Model loaded |
| `OpenAIPluginInitialized` | Plugin initialized |

---

## Metrics

### Tracked Metrics

- `total_requests`: Total API requests
- `successful_requests`: Successful requests
- `failed_requests`: Failed requests
- `success_rate`: Success percentage
- `total_input_tokens`: Input token count
- `total_output_tokens`: Output token count
- `total_duration_ms`: Total request time
- `average_duration_ms`: Average request time
- `total_cost`: Estimated cost

### Usage

```python
metrics = capability.get_metrics()
print(f"Success rate: {metrics['success_rate']}%")
print(f"Total tokens: {metrics['total_input_tokens'] + metrics['total_output_tokens']}")
```

---

## Health Checks

### Health Status

| Status | Condition |
|--------|-----------|
| `HEALTHY` | Success rate ≥ 90% |
| `DEGRADED` | Success rate < 90% |
| `UNHEALTHY` | Client not initialized |

### Check Implementation

```python
health = capability.health()
if health.healthy:
    print(f"OK - {health.message}")
else:
    print(f"ISSUE - {health.message}")
```

---

## Troubleshooting

### Common Issues

#### API Key Invalid
```
OpenAIAuthenticationError: Invalid API key
```
**Solution**: Verify your API key starts with `sk-` and is valid.

#### Rate Limit Exceeded
```
OpenAIRateLimitError: Rate limit exceeded
```
**Solution**: Implement exponential backoff or reduce request frequency.

#### Model Not Found
```
OpenAIModelError: Model not found
```
**Solution**: Check model name is correct and available in your tier.

#### Timeout
```
OpenAITimeoutError: Request timed out after 60 seconds
```
**Solution**: Increase timeout or check network connectivity.

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## References

- [Plugin Framework](../architecture/plugins.md)
- [Capability SDK](../architecture/capability-sdk.md)
- [Router](../architecture/router.md)
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
