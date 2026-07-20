"""EREN AI Tools - Tool Orchestrator Module.

Módulo de orquestación de herramientas del AI Core.

## Componentes

- **registry**: Registro de herramientas
- **executor**: Ejecutor de herramientas
- **router**: Enrutador de herramientas
- **sandbox**: Sandboxing de seguridad

## Herramientas Soportadas

| Categoría | Herramientas |
|-----------|--------------|
| DATABASE | PostgreSQL, MySQL, SQLite |
| VECTOR_STORE | Qdrant, Pinecone, Weaviate |
| MESSAGE_QUEUE | RabbitMQ, Kafka |
| API | REST, GraphQL |
| CODE | Python, JavaScript |
| WEB | HTTP, Fetch |
| FILE | Sistema de archivos |
| SYSTEM | Shell commands |
| MCP | Model Context Protocol |

## Uso

```python
from core.ai.tools import (
    ToolOrchestrator,
    ToolRegistry,
    ToolExecutor,
    ToolRouter,
    ToolDefinition,
    ToolCategory,
)

# Crear orchestrator
orchestrator = ToolOrchestrator()

# Registrar herramienta
tool = ToolDefinition(
    id="db-query",
    name="Database Query",
    description="Ejecuta queries SQL",
    category=ToolCategory.DATABASE,
)
orchestrator.registry.register(tool, implementation)

# Ejecutar
result = await orchestrator.execute(
    tool_id="db-query",
    parameters={"sql": "SELECT * FROM users"},
)

# Enrutar automáticamente
tool = orchestrator.router.route("buscar usuario por email")
if tool:
    result = await orchestrator.execute(tool.id, params)
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    TOOL ORCHESTRATOR                                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Tool Registry                             │ │
│  │              (Register, Search, Get)                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Tool Router                             │ │
│  │              (Route query to tool)                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Tool Executor                            │ │
│  │            (Execute with timeout, retries)                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Tool Sandbox                             │ │
│  │              (Security, validation)                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```
"""

from core.ai.tools.models import (
    ToolCategory,
    ToolCapability,
    ToolConfig,
    ToolDefinition,
    ToolExecution,
    ToolInterface,
    ToolParameter,
    ToolResult,
    ToolStatus,
)
from core.ai.tools.registry import (
    ToolRegistry,
    get_registry,
    set_registry,
)
from core.ai.tools.executor import ToolExecutor, SyncToolExecutor
from core.ai.tools.router import ToolRouter
from core.ai.tools.sandbox import ToolSandbox, SandboxContext


class ToolOrchestrator:
    """
    Orquestador principal de herramientas.
    
    Combina registry, executor, router y sandbox
    en una interfaz unificada.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        config: ToolConfig | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry()
        self.executor = ToolExecutor(self.registry, config)
        self.router = ToolRouter(self.registry)
        self.sandbox = ToolSandbox(
            allowed_paths=config.allowed_paths if config else None,
            blocked_commands=config.blocked_commands if config else None,
        )
        self.config = config or ToolConfig()

    async def execute(
        self,
        tool_id: str,
        parameters: dict[str, Any],
        **kwargs: Any,
    ) -> ToolResult:
        """Ejecuta una herramienta."""
        return await self.executor.execute(tool_id, parameters, **kwargs)

    def execute_sync(
        self,
        tool_id: str,
        parameters: dict[str, Any],
        **kwargs: Any,
    ) -> ToolResult:
        """Ejecuta una herramienta síncronamente."""
        sync_executor = SyncToolExecutor(self.registry, self.config)
        return sync_executor.execute(tool_id, parameters, **kwargs)

    def route(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> ToolDefinition | None:
        """Determina qué herramienta usar."""
        return self.router.route(query, context)

    async def route_and_execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> ToolResult | None:
        """Rutea y ejecuta en un paso."""
        tool = self.route(query, context)
        if not tool:
            return None
        
        params = parameters or {}
        return await self.execute(tool.id, params, **kwargs)

    def register(
        self,
        tool: ToolDefinition,
        implementation: ToolInterface | None = None,
    ) -> None:
        """Registra una herramienta."""
        self.registry.register(tool, implementation)
        
        # Registrar ruta automática
        self.router.register_route(tool.name, tool.id)

    def unregister(self, tool_id: str) -> bool:
        """Elimina una herramienta."""
        return self.registry.unregister(tool_id)

    def list_tools(
        self,
        category: ToolCategory | None = None,
    ) -> list[ToolDefinition]:
        """Lista herramientas."""
        if category:
            return self.registry.list_by_category(category)
        return self.registry.list_all()


__version__ = "1.0.0"

__all__ = [
    # Main orchestrator
    "ToolOrchestrator",
    # Models
    "ToolCategory",
    "ToolCapability",
    "ToolConfig",
    "ToolDefinition",
    "ToolExecution",
    "ToolInterface",
    "ToolParameter",
    "ToolResult",
    "ToolStatus",
    # Registry
    "ToolRegistry",
    "get_registry",
    "set_registry",
    # Executor
    "ToolExecutor",
    "SyncToolExecutor",
    # Router
    "ToolRouter",
    # Sandbox
    "ToolSandbox",
    "SandboxContext",
]
