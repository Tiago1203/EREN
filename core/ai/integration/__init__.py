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

# Domain Integration (EPIC 10)
from core.ai.integration.uow_factory import (
    AIUnitOfWork,
    AIUnitOfWorkFactory,
    get_uow_factory,
    set_uow_factory,
)

from core.ai.integration.domain_adapter import (
    DomainGatewayAdapter,
    DeviceGatewayImpl,
    IncidentGatewayImpl,
    KnowledgeGatewayImpl,
    RecommendationGatewayImpl,
    HospitalGatewayImpl,
    WorkOrderGatewayImpl,
)

from core.ai.integration.memory_bridge import (
    EntityType,
    DomainReference,
    MemoryWithReferences,
    MemoryBridge,
    create_memory_bridge,
)

from core.ai.integration.event_bridge import (
    AIEventType,
    AIEvent,
    DomainEventType,
    EventBridge,
    get_event_bridge,
    set_event_bridge,
)

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
    # Domain Integration (EPIC 10)
    "AIUnitOfWork",
    "AIUnitOfWorkFactory",
    "get_uow_factory",
    "set_uow_factory",
    "DomainGatewayAdapter",
    "DeviceGatewayImpl",
    "IncidentGatewayImpl",
    "KnowledgeGatewayImpl",
    "RecommendationGatewayImpl",
    "HospitalGatewayImpl",
    "WorkOrderGatewayImpl",
    "EntityType",
    "DomainReference",
    "MemoryWithReferences",
    "MemoryBridge",
    "create_memory_bridge",
    "AIEventType",
    "AIEvent",
    "DomainEventType",
    "EventBridge",
    "get_event_bridge",
    "set_event_bridge",
    "setup_integration",
]


def setup_integration(
    uow_factory: AIUnitOfWorkFactory | None = None,
    event_bus=None,
) -> dict:
    """
    Configura toda la integración del AI Core con el dominio.
    
    Args:
        uow_factory: Factory para UnitOfWork (opcional)
        event_bus: Event Bus del dominio (opcional)
        
    Returns:
        Dict con todas las instancias configuradas
        
    Usage:
        from core.ai.integration import setup_integration
        
        integration = setup_integration(
            uow_factory=my_factory,
            event_bus=my_event_bus,
        )
        
        device_gateway = integration["device_gateway"]
        memory_bridge = integration["memory_bridge"]
        event_bridge = integration["event_bridge"]
    """
    # Crear UnitOfWork Factory
    if uow_factory is None:
        uow_factory = get_uow_factory()
    set_uow_factory(uow_factory)
    
    # Crear Domain Adapter
    domain_adapter = DomainGatewayAdapter(uow_factory)
    
    # Crear Event Bridge
    event_bridge = get_event_bridge()
    if event_bus is not None:
        event_bridge.set_event_bus(event_bus)
    
    # Crear Gateways
    gateways = domain_adapter.create_all()
    
    # Crear Memory Bridge (sin adapter para evitar ciclos)
    from core.ai.memory import get_memory_manager
    memory_manager = get_memory_manager()
    memory_bridge = MemoryBridge(memory_manager)
    
    return {
        "uow_factory": uow_factory,
        "domain_adapter": domain_adapter,
        "event_bridge": event_bridge,
        "memory_bridge": memory_bridge,
        "gateways": gateways,
        "device_gateway": gateways["device"],
        "incident_gateway": gateways["incident"],
        "knowledge_gateway": gateways["knowledge"],
        "recommendation_gateway": gateways["recommendation"],
        "hospital_gateway": gateways["hospital"],
        "workorder_gateway": gateways["workorder"],
    }
