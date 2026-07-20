"""EREN AI Core - Cognitive Operating System Foundation.

El AI Core es el núcleo cognitivo de EREN, proporcionando la infraestructura
base sobre la cual se construyen todas las capacidades de IA.

## Módulos (EPIC 0-9)

### EPIC 0 - AI Foundation
- **kernel**: Núcleo central del AI Core
- **contracts**: Interfaces y abstracciones
- **dto**: Data Transfer Objects
- **exceptions**: Jerarquía de excepciones
- **config**: Configuración
- **registry**: Registro de modelos
- **di**: Inyección de dependencias
- **context**: Objetos de contexto

### EPIC 1 - Conversation
- **conversation**: Controlador de conversaciones

### EPIC 2 - Context Builder
- **context_builder**: Construcción de contexto inteligente

### EPIC 3 - Prompt Builder
- **prompt**: Ingeniería de prompts

### EPIC 4 - Memory Manager
- **memory**: Sistema de memoria

### EPIC 5 - Tool Orchestrator
- **tools**: Orquestación de herramientas

### EPIC 6 - Response Composer
- **response**: Composición de respuestas

### EPIC 7 - Provider Layer
- **providers**: Abstracción de proveedores LLM

### EPIC 8 - Session Management
- **sessions**: Gestión de sesiones

### EPIC 9 - AI Integration
- **integration**: Integración del AI Core

## Uso Rápido

```python
from core.ai import AICoreController, AICoreConfig

# Crear controller
config = AICoreConfig(
    default_provider="openai",
    enable_memory=True,
    enable_tools=True,
)
controller = AICoreController(config)

# Inicializar
await controller.initialize()

# Procesar solicitud
response, context = await controller.process(
    user_input="¿Cómo está mi equipo?",
    user_id="user-123",
    tenant_id="hospital-1",
)

# Ver estadísticas
stats = controller.stats
print(f"Peticiones: {stats.metrics.total_requests}")

# Apagar
await controller.shutdown()
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
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                INTEGRATION (EPIC 9)                     │ │
│  │         AICoreController - Pipeline Completo               │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```
"""

# EPIC 0 - AI Foundation
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

# EPIC 1 - Conversation
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

# EPIC 2 - Context Builder
from core.ai.context_builder import (
    ContextBuilder,
    ContextPriority,
    CompressionStrategy,
    PriorityItem,
    PriorityScore,
)
from core.ai.context_builder.models import (
    ContextBlock,
    ContextMetadata as CBContextMetadata,
    ContextSource,
    ContextPriority as CBContextPriority,
)

# EPIC 3 - Prompt Builder
from core.ai.prompt import (
    PromptBuilder,
    PromptConfig,
    PromptTemplate,
    PromptStrategy,
    RenderedPrompt,
    TemplateVariable,
)
from core.ai.prompt.models import (
    PromptType,
    PromptStrategy as PPromptStrategy,
)
from core.ai.prompt.renderer import PromptRenderer
from core.ai.prompt.optimizer import PromptOptimizer
from core.ai.prompt.strategy import (
    DirectStrategy,
    ChainOfThoughtStrategy,
    FewShotStrategy,
    TreeOfThoughtsStrategy,
)
from core.ai.prompt.versioning import PromptVersion, PromptVersionStore

# EPIC 4 - Memory Manager
from core.ai.memory import (
    MemoryManager,
    MemoryItem,
    MemoryType,
    MemoryRepository,
    InMemoryMemoryRepository,
)
from core.ai.memory.models import (
    MemoryConfig,
    MemoryStats,
)
from core.ai.memory.repository import MemoryRepository

# EPIC 5 - Tool Orchestrator
from core.ai.tools import (
    ToolOrchestrator,
    ToolRegistry,
    ToolExecutor,
    ToolRouter,
    ToolSandbox,
    ToolCategory,
    ToolCapability,
    ToolConfig,
    ToolDefinition,
    ToolExecution,
    ToolInterface,
    ToolParameter,
    ToolResult,
    ToolStatus,
    get_registry,
    set_registry,
)
from core.ai.tools.models import StreamChunk as ToolStreamChunk

# EPIC 6 - Response Composer
from core.ai.response import (
    ResponseComposer,
    StreamingResponseComposer,
    ResponseFormatter,
    Response,
    ResponseElement,
    ResponseElementType,
    ResponseStatus,
    ResponseType,
    ResponseConfig,
    StreamChunk as RespStreamChunk,
    CodeBlock,
    Reference,
    TableColumn,
    TableData,
    ChartConfig,
)

# EPIC 7 - Provider Layer
from core.ai.providers import (
    ProviderManager,
    RateLimiter,
    OpenAIProvider,
    AnthropicProvider,
    ProviderType,
    ModelCapability,
    ModelInfo as ProviderModelInfo,
    TokenUsage,
    ChatMessage,
    ToolCall as ProviderToolCall,
    CompletionResult,
    ChatCompletionResult,
    ProviderStreamChunk,
    ProviderConfig,
    UsageRecord,
    ProviderStats,
)

# EPIC 8 - Session Management
from core.ai.sessions import (
    SessionManager,
    Session,
    SessionContext,
    SessionEvent,
    SessionStats,
    SessionStatus,
    Message as SessionMessage,
    TokenBudget,
    ConversationLimit,
)

# EPIC 9 - AI Integration
from core.ai.integration import (
    AICoreController,
    AICoreConfig,
    AICoreMetrics,
    AICoreStats,
    AICoreStatus,
    ProcessingContext,
    ProcessingState,
)

__version__ = "1.0.0"

__all__ = [
    # ========== EPIC 0 - AI Foundation ==========
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
    
    # ========== EPIC 1 - Conversation ==========
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
    
    # ========== EPIC 2 - Context Builder ==========
    "ContextBuilder",
    "ContextPriority",
    "CompressionStrategy",
    "PriorityItem",
    "PriorityScore",
    "ContextBlock",
    "CBContextMetadata",
    "ContextSource",
    "CBContextPriority",
    
    # ========== EPIC 3 - Prompt Builder ==========
    "PromptBuilder",
    "PromptConfig",
    "PromptTemplate",
    "PromptStrategy",
    "RenderedPrompt",
    "TemplateVariable",
    "PromptType",
    "PPromptStrategy",
    "PromptRenderer",
    "PromptOptimizer",
    "DirectStrategy",
    "ChainOfThoughtStrategy",
    "FewShotStrategy",
    "TreeOfThoughtsStrategy",
    "PromptVersion",
    "PromptVersionStore",
    
    # ========== EPIC 4 - Memory Manager ==========
    "MemoryManager",
    "MemoryItem",
    "MemoryType",
    "MemoryRepository",
    "InMemoryMemoryRepository",
    "MemoryConfig",
    "MemoryStats",
    
    # ========== EPIC 5 - Tool Orchestrator ==========
    "ToolOrchestrator",
    "ToolRegistry",
    "ToolExecutor",
    "ToolRouter",
    "ToolSandbox",
    "ToolCategory",
    "ToolCapability",
    "ToolConfig",
    "ToolDefinition",
    "ToolExecution",
    "ToolInterface",
    "ToolParameter",
    "ToolResult",
    "ToolStatus",
    "get_registry",
    "set_registry",
    "ToolStreamChunk",
    
    # ========== EPIC 6 - Response Composer ==========
    "ResponseComposer",
    "StreamingResponseComposer",
    "ResponseFormatter",
    "Response",
    "ResponseElement",
    "ResponseElementType",
    "ResponseStatus",
    "ResponseType",
    "ResponseConfig",
    "RespStreamChunk",
    "CodeBlock",
    "Reference",
    "TableColumn",
    "TableData",
    "ChartConfig",
    
    # ========== EPIC 7 - Provider Layer ==========
    "ProviderManager",
    "RateLimiter",
    "OpenAIProvider",
    "AnthropicProvider",
    "ProviderType",
    "ModelCapability",
    "ProviderModelInfo",
    "TokenUsage",
    "ChatMessage",
    "ProviderToolCall",
    "CompletionResult",
    "ChatCompletionResult",
    "ProviderStreamChunk",
    "ProviderConfig",
    "UsageRecord",
    "ProviderStats",
    
    # ========== EPIC 8 - Session Management ==========
    "SessionManager",
    "Session",
    "SessionContext",
    "SessionEvent",
    "SessionStats",
    "SessionStatus",
    "SessionMessage",
    "TokenBudget",
    "ConversationLimit",
    
    # ========== EPIC 9 - AI Integration ==========
    "AICoreController",
    "AICoreConfig",
    "AICoreMetrics",
    "AICoreStats",
    "AICoreStatus",
    "ProcessingContext",
    "ProcessingState",
]
