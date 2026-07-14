# Cognitive Model Registry (CMR)

> **Philosophy**: Providers offer models. The Cognitive Kernel never knows specific models. All decisions about models are made through the Model Registry.

This document describes the Cognitive Model Registry, the official system for registering, discovering, and managing LLM models in EREN OS.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Model Descriptor](#model-descriptor)
4. [Categories](#categories)
5. [Capabilities](#capabilities)
6. [Selection Policies](#selection-policies)
7. [Model Catalog](#model-catalog)
8. [Integration](#integration)
9. [Events](#events)
10. [Metrics](#metrics)

---

## Overview

The Model Registry provides a centralized system for managing all LLM models in EREN.

### Key Features

- **Model Registration**: Register models from any provider
- **Model Discovery**: Find models by capabilities, category, or provider
- **Dynamic Selection**: Select best model based on policies
- **Capability Matching**: Match models to task requirements
- **Metrics Tracking**: Track usage and performance

---

## Architecture

### Module Structure

```
core/models/
├── __init__.py           # Exports
├── descriptor.py         # ModelDescriptor
├── registry.py          # ModelRegistry
├── selector.py          # ModelSelector
├── catalog.py           # ModelCatalog
├── types.py             # Types and enums
├── exceptions.py        # Exception types
└── README.md           # Quick start
```

### Components

| Component | Description |
|-----------|-------------|
| `ModelDescriptor` | Contains all model metadata |
| `ModelRegistry` | Manages registration and discovery |
| `ModelSelector` | Implements selection strategies |
| `ModelCatalog` | Pre-defined model descriptors |

### Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Multi Provider Layer                             │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   Cognitive Model Registry
┌──────────────────────────────────────────────────────────────────────┐
│ Registry │ Catalog │ Discovery │ Selector │ Policies │ Metrics │     │
└──────────────────────────────────────────────────────────────────────┘
                              │
        ┌──────────────┬──────────────┬──────────────┐
        ▼              ▼              ▼
     OpenAI         Claude        Ollama
```

---

## Model Descriptor

Each model registered contains:

```python
@dataclass
class ModelDescriptor:
    # Identification
    model_id: str
    provider_id: str
    display_name: str
    version: str

    # Context and limits
    context_window: int
    max_output_tokens: int

    # Capabilities
    supports_streaming: bool
    supports_function_calling: bool
    supports_json_mode: bool
    supports_multimodal: bool
    supports_reasoning: bool
    supports_embeddings: bool
    supports_vision: bool
    supports_audio: bool
    supports_tools: bool

    # Category
    category: ModelCategory

    # Pricing
    pricing: ModelPricing

    # Availability
    availability: ModelAvailability
```

---

## Categories

| Category | Description |
|---------|-------------|
| `GENERAL` | General purpose models |
| `REASONING` | Optimized for reasoning tasks |
| `VISION` | Vision-capable models |
| `EMBEDDING` | Embedding models |
| `CODE` | Code generation models |
| `MEDICAL` | Medical/healthcare models |
| `MULTIMODAL` | Multi-modal models |
| `AUDIO` | Audio processing models |
| `CUSTOM` | Custom/proprietary models |

---

## Capabilities

Each model announces:

| Capability | Description |
|------------|-------------|
| `reasoning` | Advanced reasoning capabilities |
| `tool_calling` | Function/tool calling |
| `json_output` | Structured JSON output |
| `vision` | Image understanding |
| `streaming` | Streaming responses |
| `embeddings` | Text embeddings |
| `function_calling` | Function calling |
| `long_context` | >100K context window |
| `image_understanding` | Image analysis |
| `audio_understanding` | Audio processing |
| `multimodal` | Multi-modal support |

---

## Selection Policies

| Policy | Description | Use Case |
|--------|-------------|----------|
| `DEFAULT` | Use default model | Simple deployments |
| `FASTEST` | Lowest latency | Real-time applications |
| `CHEAPEST` | Lowest cost | Cost optimization |
| `HIGHEST_QUALITY` | Best quality score | Quality-critical tasks |
| `LONGEST_CONTEXT` | Largest context window | Long document processing |
| `REASONING` | Optimized for reasoning | Complex reasoning tasks |
| `MULTIMODAL` | Best multimodal | Vision + text tasks |

### Usage

```python
from core.models import ModelRegistry, ModelSelector, ModelSelectionPolicy

registry = ModelRegistry()
registry.register_from_catalog()

selector = ModelSelector(registry)

# Select for reasoning
model = selector.select(ModelSelectionPolicy.REASONING)

# Select with requirements
model = selector.select(
    policy=ModelSelectionPolicy.MULTIMODAL,
    capabilities=["vision", "json_output"],
)
```

---

## Model Catalog

Pre-defined models for common providers:

### OpenAI

| Model | Context | Max Output | Capabilities |
|-------|---------|------------|--------------|
| `gpt-5` | 128K | 16K | Reasoning, Vision, Tools |
| `gpt-5-mini` | 64K | 8K | Reasoning, Vision, Tools |
| `gpt-5-nano` | 32K | 4K | Reasoning, Tools |
| `gpt-4-turbo` | 128K | 16K | Vision, Tools |
| `gpt-4o` | 128K | 16K | Vision, Tools |
| `gpt-4o-mini` | 128K | 8K | Vision, Tools |

### Claude

| Model | Context | Max Output | Capabilities |
|-------|---------|------------|--------------|
| `claude-sonnet-4` | 200K | 8K | Reasoning, Vision, Tools |
| `claude-opus-4` | 200K | 8K | Reasoning, Vision, Tools |
| `claude-haiku-3` | 200K | 4K | Reasoning, Vision, Tools |

### Ollama (Local)

| Model | Context | Max Output | Capabilities |
|-------|---------|------------|--------------|
| `llama3.1:70b` | 128K | 4K | Reasoning |
| `llama3.1:8b` | 128K | 4K | Reasoning |
| `mistral:7b` | 32K | 4K | - |
| `qwen2:72b` | 128K | 8K | Multimodal |

### Gemini

| Model | Context | Max Output | Capabilities |
|-------|---------|------------|--------------|
| `gemini-2.5-pro` | 2M | 32K | Reasoning, Vision, Tools |
| `gemini-2.5-flash` | 1M | 16K | Reasoning, Vision, Tools |

---

## Integration

### With Provider Layer

```python
from core.models import ModelRegistry
from core.providers import ProviderManager

# Get model from registry
model = registry.get("gpt-5-mini")

# Use with provider
manager = ProviderManager()
response = manager.generate(
    GenerationRequest(
        prompt="...",
        model=model.model_id,
    )
)
```

### With Capability SDK

```python
from core.sdk import CapabilityContext
from core.models import ModelRegistry

registry = ModelRegistry()
registry.register_from_catalog()

# Select model for task
selector = ModelSelector(registry)
model = selector.select(
    capabilities=["reasoning", "json_output"]
)

# Use in capability
context = CapabilityContext(
    capability_id="reasoning",
    metadata={"model_id": model.model_id},
)
```

### With Diagnostics

```python
from core.diagnostics import ERENDiagnostics

report = ERENDiagnostics().run_full_system_validation()

# Check model registry health
models = report.section("models")
print(f"Models registered: {models.count}")
```

---

## Events

| Event | Description |
|-------|-------------|
| `ModelRegistered` | Model registered |
| `ModelDiscovered` | Model discovered |
| `ModelSelected` | Model selected for task |
| `ModelUnavailable` | Model became unavailable |
| `ModelUpdated` | Model metadata updated |
| `ModelRemoved` | Model unregistered |

---

## Metrics

### Tracked Metrics

- `total_requests`: Total requests to model
- `successful_requests`: Successful requests
- `failed_requests`: Failed requests
- `success_rate`: Success percentage
- `total_input_tokens`: Input tokens used
- `total_output_tokens`: Output tokens generated
- `average_latency_ms`: Average response time
- `total_cost`: Estimated cost

### Usage

```python
metrics = model.metrics.to_dict()

print(f"Success rate: {metrics['success_rate']:.1f}%")
print(f"Average latency: {metrics['average_latency_ms']:.0f}ms")
print(f"Total cost: ${metrics['total_cost']:.4f}")
```

---

## References

- [Multi-Provider Layer](./providers.md)
- [Runtime Architecture](./runtime.md)
- [Capability SDK](./capability-sdk.md)
- [Plugin Framework](./plugins.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
