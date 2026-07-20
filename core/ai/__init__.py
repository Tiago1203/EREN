"""EREN AI Core - Cognitive Operating System Foundation.

El AI Core es el núcleo cognitivo de EREN, proporcionando la infraestructura
base sobre la cual se construyen todas las capacidades de IA.

## Módulos

### EPIC 0 - AI Foundation
- **kernel**: Núcleo central del AI Core
- **contracts**: Interfaces y abstracciones
- **dto**: Data Transfer Objects
- **exceptions**: Jerarquía de excepciones
- **config**: Configuración
- **registry**: Registro de modelos
- **providers**: Abstracción de proveedores
- **di**: Inyección de dependencias
- **context**: Objetos de contexto

### EPIC 1 - Conversation
- **conversation**: Controlador de conversaciones

## Uso

```python
from core.ai import AIKernel
from core.ai.conversation import ConversationController

# AI Kernel
kernel = AIKernel()
await kernel.initialize()
response = await kernel.process(request)

# Conversation Controller
controller = ConversationController()
conversation = controller.create_conversation(
    tenant_id="tenant-1",
    title="Support Chat",
)
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        AI CORE                                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   AI FOUNDATION (EPIC 0)                   │ │
│  │     Kernel, Contracts, DTOs, Config, Registry, etc.       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                CONVERSATION (EPIC 1)                     │ │
│  │    Controller, Lifecycle, Repository, Events           │ │
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

# Conversation module (EPIC 1)
from core.ai.conversation import (
    ConversationController,
    ConversationLifecycle,
    SessionLifecycle,
    Conversation,
    ConversationContext,
    ConversationMetadata,
    ConversationMessage,
    ConversationParticipant,
    ConversationSession,
    ConversationState,
    ConversationType,
    ConversationRepository,
    InMemoryConversationRepository,
    ConversationEvent,
    ConversationEventDispatcher,
    ConversationEventType,
    get_event_dispatcher,
    reset_event_dispatcher,
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
    # Conversation (EPIC 1)
    "ConversationController",
    "ConversationLifecycle",
    "SessionLifecycle",
    "Conversation",
    "ConversationContext",
    "ConversationMetadata",
    "ConversationMessage",
    "ConversationParticipant",
    "ConversationSession",
    "ConversationState",
    "ConversationType",
    "ConversationRepository",
    "InMemoryConversationRepository",
    "ConversationEvent",
    "ConversationEventDispatcher",
    "ConversationEventType",
    "get_event_dispatcher",
    "reset_event_dispatcher",
]
