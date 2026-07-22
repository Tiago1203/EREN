# EREN OS Cognitive Model Registry (CMR)

The official system for registering, discovering, and managing LLM models in EREN OS.

## Quick Start

```python
from core.models import (
    ModelRegistry,
    ModelSelector,
    ModelCatalog,
    ModelSelectionPolicy,
)

# Create registry
registry = ModelRegistry()

# Register models from catalog
registry.register_from_catalog()

# Select model
selector = ModelSelector(registry)
model = selector.select(ModelSelectionPolicy.REASONING)

print(f"Selected: {model.display_name}")
```

## Features

- **9 Model Categories**: GENERAL, REASONING, VISION, MEDICAL, etc.
- **8 Selection Policies**: DEFAULT, FASTEST, CHEAPEST, HIGHEST_QUALITY, etc.
- **15+ Pre-defined Models**: GPT-5, Claude, Llama, Gemini
- **Dynamic Discovery**: Find models by capabilities
- **Metrics Tracking**: Usage and performance

## Documentation

See [docs/architecture/model-registry.md](../../docs/architecture/model-registry.md) for complete documentation.

## License

EREN OS License
