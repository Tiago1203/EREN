"""EREN AI Core - Cognitive Operating System Foundation.

El AI Core es el núcleo cognitivo de EREN, proporcionando la infraestructura
base sobre la cual se construyen todas las capacidades de IA.

## Módulos

- **kernel**: Núcleo central del AI Core
- **contracts**: Interfaces y abstracciones
- **dto**: Data Transfer Objects
- **exceptions**: Jerarquía de excepciones
- **config**: Configuración
- **registry**: Registro de modelos
- **providers**: Abstracción de proveedores
- **di**: Inyección de dependencias
- **context**: Objetos de contexto

## Uso

```python
from core.ai import AIKernel

# Create and initialize kernel
kernel = AIKernel()
await kernel.initialize()

# Process requests
response = await kernel.process(request)

# Stream responses
async for chunk in kernel.stream(request):
    print(chunk.content)
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        AI KERNEL                                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  AI Configuration                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │  Model      │ │  Provider    │ │    Dependency        │ │
│  │  Registry   │ │  Router      │ │    Injection         │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  AI Context Manager                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```
"""

from core.ai.kernel import AIKernel, get_kernel, shutdown_kernel, reset_kernel
from core.ai.config import AIConfiguration, DictAIConfiguration, FileAIConfiguration
from core.ai.contracts import (
    AIProvider,
    ModelRegistry,
    Container,
    Scope,
    Tool,
    ToolRegistry,
)
from core.ai.di import get_container, set_container, reset_container
from core.ai.context import AIContextManager
from core.ai.dto import (
    AIRequest,
    AIResponse,
    AIContext,
    Message,
    MessageRole,
    Content,
    ContentType,
    ModelInfo,
    ProviderInfo,
    StreamChunk,
    UsageInfo,
    ToolDefinition,
    ToolCall,
    ToolResult,
    ContextMetadata,
    HealthReport,
    HealthStatus,
)
from core.ai.exceptions import (
    AIError,
    AIConfigurationError,
    AIProviderError,
    AIProviderNotFoundError,
    AIModelError,
    AIModelNotFoundError,
    AIContextError,
    AIValidationError,
    AIInjectionError,
    AIInitializationError,
    AIProcessingError,
    AITimeoutError,
    AIRateLimitError,
    AIAuthenticationError,
    AIQuotaExceededError,
)
from core.ai.registry import ModelRegistry, ProviderRegistry
from core.ai.providers import (
    BaseProvider,
    ProviderFactory,
    OpenAIProvider,
    AnthropicProvider,
    AzureOpenAIProvider,
    ProviderRouter,
)

__version__ = "1.0.0"

__all__ = [
    # Kernel
    "AIKernel",
    "get_kernel",
    "shutdown_kernel",
    "reset_kernel",
    # Configuration
    "AIConfiguration",
    "DictAIConfiguration",
    "FileAIConfiguration",
    # Contracts
    "AIProvider",
    "ModelRegistry",
    "Container",
    "Scope",
    "Tool",
    "ToolRegistry",
    # DI
    "get_container",
    "set_container",
    "reset_container",
    # Context
    "AIContextManager",
    # DTOs
    "AIRequest",
    "AIResponse",
    "AIContext",
    "Message",
    "MessageRole",
    "Content",
    "ContentType",
    "ModelInfo",
    "ProviderInfo",
    "StreamChunk",
    "UsageInfo",
    "ToolDefinition",
    "ToolCall",
    "ToolResult",
    "ContextMetadata",
    "HealthReport",
    "HealthStatus",
    # Exceptions
    "AIError",
    "AIConfigurationError",
    "AIProviderError",
    "AIProviderNotFoundError",
    "AIModelError",
    "AIModelNotFoundError",
    "AIContextError",
    "AIValidationError",
    "AIInjectionError",
    "AIInitializationError",
    "AIProcessingError",
    "AITimeoutError",
    "AIRateLimitError",
    "AIAuthenticationError",
    "AIQuotaExceededError",
    # Registry
    "ProviderRegistry",
    # Providers
    "BaseProvider",
    "ProviderFactory",
    "OpenAIProvider",
    "AnthropicProvider",
    "AzureOpenAIProvider",
    "ProviderRouter",
]
