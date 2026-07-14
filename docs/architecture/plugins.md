# EREN OS Cognitive Plugin Framework

> **Philosophy**: The Cognitive Kernel should never be modified to add new capabilities. All future capabilities must be incorporated as Cognitive Plugins.

This document describes the Cognitive Plugin Framework (CPF), the official extensibility system for EREN.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Plugin Lifecycle](#plugin-lifecycle)
4. [Plugin Types](#plugin-types)
5. [Manifest Format](#manifest-format)
6. [Usage](#usage)
7. [Integration](#integration)
8. [Observability](#observability)
9. [Roadmap](#roadmap)

---

## Overview

The Cognitive Plugin Framework enables EREN to incorporate new capabilities without modifying the core Kernel.

### Supported Capabilities

- LLMs
- RAG systems
- Knowledge bases
- FHIR connectors
- PACS integration
- HL7 interfaces
- Biomedical devices
- Hospital systems
- External APIs
- Clinical algorithms
- Vision engines
- Speech processing
- OCR

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Runtime                                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Cognitive Plugin Manager                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Manager         │  │  Registry        │  │  Loader         │  │
│  │                  │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Events          │  │  Metrics         │  │  Trace          │  │
│  │                  │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  LLM Plugin  │    │ Medical      │    │   Device     │
│              │    │ Plugin       │    │   Plugin     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Cognitive Contracts                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Structure

```
core/plugins/
├── __init__.py           # Main exports
├── manager.py            # PluginManager (main engine)
├── descriptor.py         # PluginDescriptor
├── context.py           # PluginContext
├── loader.py            # PluginLoader
├── registry.py          # PluginRegistry
├── manifest.py          # Manifest parsing
├── events.py            # Event publishing
├── metrics.py           # Metrics collection
├── trace.py             # Tracing
├── types.py             # Types and enums
└── exceptions.py         # All exceptions
```

---

## Plugin Lifecycle

```
DISCOVER
   │
   ▼
VALIDATE
   │
   ▼
LOAD
   │
   ▼
INITIALIZE
   │
   ▼
REGISTER
   │
   ▼
ACTIVATE
   │
   ▼
READY (ACTIVE)
   │
   ├── PAUSE
   │
   ▼
   RELOAD
   │
   ▼
   UNLOAD
```

### States

| State | Description |
|-------|-------------|
| `DISCOVERED` | Plugin manifest found |
| `REGISTERED` | Plugin registered in registry |
| `LOADED` | Plugin code loaded |
| `INITIALIZED` | Plugin initialized |
| `ACTIVE` | Plugin fully operational |
| `PAUSED` | Plugin temporarily paused |
| `FAILED` | Plugin encountered error |
| `UNLOADED` | Plugin unloaded |

---

## Plugin Types

### Categories

| Category | Description |
|----------|-------------|
| `COGNITIVE` | Core cognitive capabilities |
| `LLM` | Language model integrations |
| `KNOWLEDGE` | Knowledge base integrations |
| `MEMORY` | Memory systems |
| `DEVICE` | Biomedical devices |
| `FHIR` | FHIR interoperability |
| `HL7` | HL7 messaging |
| `PACS` | Medical imaging |
| `TOOLS` | Tool integrations |
| `CONNECTOR` | External connectors |
| `CUSTOM` | Custom plugins |

### Priority Levels

| Priority | Value | Use Case |
|----------|-------|----------|
| `CRITICAL` | 200 | System-critical |
| `HIGH` | 150 | High importance |
| `NORMAL` | 100 | Default |
| `LOW` | 50 | Background tasks |
| `BACKGROUND` | 10 | Optional |

---

## Manifest Format

### Example Manifest

```json
{
  "plugin_id": "openai-llm",
  "version": "1.0.0",
  "name": "OpenAI LLM Plugin",
  "description": "OpenAI GPT integration",
  "author": "EREN Team",
  "category": "llm",
  "priority": 100,
  "contracts": [
    "ReasoningContract",
    "SummarizationContract"
  ],
  "dependencies": [
    "memory-contract"
  ],
  "capabilities": [
    "reasoning",
    "summarization",
    "chat"
  ],
  "configuration": {
    "api_key": "...",
    "model": "gpt-4"
  }
}
```

### Builder Pattern

```python
from core.plugins import PluginManifestBuilder, PluginCategory

manifest = (
    PluginManifestBuilder()
    .plugin_id("my-plugin")
    .version("1.0.0")
    .name("My Plugin")
    .category(PluginCategory.LLM)
    .implements("ReasoningContract")
    .depends_on("memory-contract")
    .provides("reasoning")
    .build()
)
```

---

## Usage

### Basic Plugin Creation

```python
from core.plugins import PluginManager, PluginState

manager = PluginManager()

# Discover plugin
descriptor = manager.discover({
    "plugin_id": "my-plugin",
    "version": "1.0.0",
    "name": "My Plugin",
})

# Register
manager.register(descriptor)

# Activate
manager.activate("my-plugin")
```

### With Dependency

```python
# Discover plugins
plugin_a = manager.discover(manifest_a)
plugin_b = manager.discover(manifest_b)

# Register in dependency order
manager.register(plugin_a)
manager.register(plugin_b)

# Activate in dependency order
manager.activate("plugin-a")
manager.activate("plugin-b")
```

### Bulk Operations

```python
# Activate all plugins
results = manager.activate_all()

# Deactivate all plugins
results = manager.deactivate_all()
```

---

## Integration

### With DI Container

```python
from core.container import CognitiveContainer

container = CognitiveContainer()
container.register("PluginManager", PluginManager)

# Plugins can access container via context
def on_initialize(self, context):
    container = context.container
    # Use services
```

### With Capability Registry

```python
# Plugins can register capabilities
def on_activate(self):
    self.capability_registry.register("my-capability", self)
```

---

## Observability

### Events

Plugin publishes events:

| Event | Description |
|-------|-------------|
| `PluginDiscovered` | Plugin discovered |
| `PluginRegistered` | Plugin registered |
| `PluginLoaded` | Plugin loaded |
| `PluginActivated` | Plugin activated |
| `PluginFailed` | Plugin failed |

### Metrics

```python
from core.plugins import get_plugin_metrics

metrics = get_plugin_metrics()
summary = metrics.get_summary()

print(f"Plugins loaded: {summary['load_stats']['total_loaded']}")
print(f"Failures: {summary['load_stats']['total_failures']}")
```

### Tracing

```python
from core.plugins import get_plugin_trace

trace = get_plugin_trace()
entries = trace.get_entries_by_plugin("my-plugin")
```

---

## Roadmap

### Phase 1: Core Infrastructure ✓
- [x] PluginManager
- [x] PluginRegistry
- [x] PluginLoader
- [x] PluginManifest
- [x] Events
- [x] Metrics
- [x] Tracing

### Phase 2: Plugin System
- [ ] Plugin validation framework
- [ ] Plugin sandboxing
- [ ] Hot reload support
- [ ] Plugin versioning

### Phase 3: Standard Plugins
- [ ] OpenAI LLM Plugin
- [ ] FHIR Connector Plugin
- [ ] Memory Plugin
- [ ] Knowledge Base Plugin

---

## References

- [Architecture Overview](./architecture-overview.md)
- [Runtime Documentation](./runtime.md)
- [Capability Registry](./capability-registry.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
