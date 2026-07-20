# EREN OS Multi-Provider Layer (CMPL)

The official abstraction layer for LLM providers in EREN OS.

## Quick Start

```python
from core.providers import (
    ProviderManager,
    ProviderConfig,
    ProviderType,
    GenerationRequest,
)

# Create manager
manager = ProviderManager()

# Add providers
manager.add_provider(OpenAIProvider(), ProviderConfig(
    provider_id="openai-primary",
    provider_type=ProviderType.OPENAI,
    enabled=True,
    priority=1,
))

# Generate
response = manager.generate(GenerationRequest(prompt="Hello"))
print(response.content)
```

## Features

- **7 Selection Policies**: DEFAULT, PRIORITY, ROUND_ROBIN, HEALTHY_FIRST, LOWEST_LATENCY, FAILOVER, RANDOM
- **6 Provider Types**: OpenAI, Claude, Ollama, Gemini, Azure OpenAI, Custom
- **Automatic Failover**: Fallback on provider failure
- **Health Monitoring**: Real-time health checks
- **Metrics**: Request tracking and cost analysis

## Documentation

See [docs/architecture/providers.md](../../docs/architecture/providers.md) for complete documentation.

## License

EREN OS License
