# OpenAI Cognitive Capability Plugin

> **Philosophy**: The Cognitive Kernel does not know OpenAI. OpenAI is only a cognitive capability registered as a Plugin.

This plugin provides OpenAI GPT reasoning capability for EREN using the Cognitive Plugin Framework and Capability SDK.

## Features

- **Reasoning Capability**: Implements `ReasoningContract` for cognitive reasoning
- **Multiple Models**: Supports GPT-5, GPT-4, and variants
- **Plugin Integration**: Registered with the Plugin Framework
- **SDK Compatible**: Uses the Capability SDK for lifecycle management
- **Full Observability**: Events, metrics, and tracing

## Installation

```bash
pip install openai
```

## Configuration

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

## Usage

### Direct Usage

```python
from core.sdk import CapabilityContext, CapabilityResult

# Initialize
context = CapabilityContext(capability_id="openai-reasoning")
capability.initialize(context)

# Execute
context = CapabilityContext(
    prompt="Explain quantum computing in simple terms.",
    system_prompt="You are a helpful assistant.",
)
result = capability.execute(context)

print(result.data["content"])
```

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

### With Router

```python
from core.router import CapabilityRouter

router = CapabilityRouter()
router.register_route("reasoning", "openai-reasoning")

selected = router.select("reasoning")
```

## Supported Models

| Model | Context Window | Max Output | Vision | Function Calling |
|-------|---------------|------------|--------|------------------|
| gpt-5 | 128K | 16K | ✅ | ✅ |
| gpt-5-mini | 64K | 8K | ✅ | ✅ |
| gpt-5-nano | 32K | 4K | ❌ | ✅ |
| gpt-4 | 128K | 8K | ❌ | ✅ |
| gpt-4-turbo | 128K | 16K | ✅ | ✅ |
| gpt-4o | 128K | 16K | ✅ | ✅ |
| gpt-4o-mini | 128K | 8K | ✅ | ✅ |

## Environment Variables

```bash
export OPENAI_API_KEY="sk-your-api-key"
```

## Metrics

The plugin tracks:
- Total requests
- Successful/failed requests
- Token usage (input/output)
- Request duration
- Estimated cost

```python
metrics = capability.get_metrics()
print(f"Success rate: {metrics['success_rate']}%")
print(f"Total tokens: {metrics['total_input_tokens'] + metrics['total_output_tokens']}")
```

## Events

The plugin publishes:
- `OpenAIRequestStarted`
- `OpenAIRequestCompleted`
- `OpenAIRequestFailed`
- `OpenAIModelLoaded`
- `OpenAIPluginInitialized`

## License

MIT
