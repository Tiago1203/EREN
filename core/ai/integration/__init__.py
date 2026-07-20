"""EREN AI Core - Integration Module.

Módulo de integración del AI Core de EREN.

Este módulo integra todos los componentes del AI Core:

```
┌─────────────────────────────────────────────────────────────┐
│                     AI CORE CONTROLLER                                  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              CONVERSATION CONTROLLER                       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│  ┌──────────┬──────────┬──┴──┬──────────┬──────────┐ │
│  │          │          │     │          │          │ │
│  ▼          ▼          ▼     ▼          ▼          ▼ │
│ Memory    Prompt    Context Tools    Providers  Sessions │
│ Manager   Builder   Builder Orchestrator Layer    Manager │
│                                                               │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              RESPONSE COMPOSER                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Uso

```python
from core.ai.integration import AICoreController, AICoreConfig

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

# Procesar con streaming
async for chunk in controller.process_stream(
    user_input="Dame el reporte",
    user_id="user-123",
):
    print(chunk.content, end="")

# Ver estadísticas
stats = controller.stats
print(f"Peticiones: {stats.metrics.total_requests}")
print(f"Éxito: {stats.metrics.success_rate}")

# Apagar
await controller.shutdown()
```

## Componentes Integrados

| Componente | Descripción |
|-----------|-------------|
| ConversationController | Gestión de conversaciones |
| MemoryManager | Sistema de memoria |
| PromptBuilder | Construcción de prompts |
| ContextBuilder | Construcción de contexto |
| ToolOrchestrator | Orquestación de herramientas |
| ProviderManager | Gestión de proveedores |
| ResponseComposer | Composición de respuestas |
| SessionManager | Gestión de sesiones |
"""

from core.ai.integration.models import (
    AICoreConfig,
    AICoreMetrics,
    AICoreStats,
    AICoreStatus,
    ProcessingContext,
    ProcessingState,
)
from core.ai.integration.controller import AICoreController

__version__ = "1.0.0"

__all__ = [
    # Models
    "AICoreConfig",
    "AICoreMetrics",
    "AICoreStats",
    "AICoreStatus",
    "ProcessingContext",
    "ProcessingState",
    # Controller
    "AICoreController",
]
