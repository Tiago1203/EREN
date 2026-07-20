"""AI Contracts - Interfaces y abstracciones del AI Core."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Protocol, runtime_checkable

from core.ai.dto import (
    AIRequest,
    AIResponse,
    HealthReport,
    Message,
    ModelCapabilities,
    ModelInfo,
    ProviderInfo,
    StreamChunk,
    ToolDefinition,
    ToolResult,
)


# ============== Provider Contracts ==============

@runtime_checkable
class AIProvider(ABC):
    """Contrato base para proveedores de IA."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """ID único del proveedor."""
        ...

    @property
    @abstractmethod
    def provider_info(self) -> ProviderInfo:
        """Información del proveedor."""
        ...

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> None:
        """Inicializa el proveedor con la configuración."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Apaga el proveedor limpiamente."""
        ...

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        """Genera una respuesta."""
        ...

    @abstractmethod
    async def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        """Genera una respuesta en streaming."""
        ...

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """Lista los modelos disponibles."""
        ...

    @abstractmethod
    async def get_model(self, model_id: str) -> ModelInfo | None:
        """Obtiene información de un modelo específico."""
        ...

    @abstractmethod
    async def health_check(self) -> HealthReport:
        """Verifica la salud del proveedor."""
        ...


class StreamingProvider(AIProvider):
    """Mixin para proveedores que soportan streaming."""

    @abstractmethod
    async def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        """Genera una respuesta en streaming."""
        ...


class FunctionCallingProvider(AIProvider):
    """Mixin para proveedores que soportan function calling."""

    @abstractmethod
    async def generate_with_functions(
        self,
        request: AIRequest,
        functions: list[ToolDefinition],
    ) -> AIResponse:
        """Genera una respuesta usando function calling."""
        ...

    @abstractmethod
    async def stream_with_functions(
        self,
        request: AIRequest,
        functions: list[ToolDefinition],
    ) -> AsyncIterator[StreamChunk]:
        """Genera una respuesta en streaming usando function calling."""
        ...


# ============== Model Registry Contracts ==============

@runtime_checkable
class ModelRegistry(ABC):
    """Contrato para registro de modelos."""

    @abstractmethod
    def register_model(self, model: ModelInfo) -> None:
        """Registra un nuevo modelo."""
        ...

    @abstractmethod
    def unregister_model(self, model_id: str) -> bool:
        """Elimina un modelo del registro."""
        ...

    @abstractmethod
    def get_model(self, model_id: str) -> ModelInfo | None:
        """Obtiene información de un modelo."""
        ...

    @abstractmethod
    def list_models(self, provider: str | None = None) -> list[ModelInfo]:
        """Lista todos los modelos, opcionalmente filtrados por proveedor."""
        ...

    @abstractmethod
    def find_models(
        self,
        capability: str | None = None,
        max_tokens: int | None = None,
    ) -> list[ModelInfo]:
        """Encuentra modelos que cumplan ciertos criterios."""
        ...

    @abstractmethod
    def get_default_model(self) -> ModelInfo | None:
        """Obtiene el modelo por defecto."""
        ...

    @abstractmethod
    def set_default_model(self, model_id: str) -> None:
        """Establece el modelo por defecto."""
        ...


# ============== Configuration Contracts ==============

@runtime_checkable
class AIConfiguration(ABC):
    """Contrato para configuración del AI Core."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Establece un valor de configuración."""
        ...

    @abstractmethod
    def get_provider_config(self, provider_id: str) -> dict[str, Any] | None:
        """Obtiene la configuración de un proveedor."""
        ...

    @abstractmethod
    def set_provider_config(self, provider_id: str, config: dict[str, Any]) -> None:
        """Establece la configuración de un proveedor."""
        ...

    @abstractmethod
    def get_model_config(self, model_id: str) -> dict[str, Any] | None:
        """Obtiene la configuración de un modelo."""
        ...

    @abstractmethod
    def set_model_config(self, model_id: str, config: dict[str, Any]) -> None:
        """Establece la configuración de un modelo."""
        ...

    @abstractmethod
    def validate(self) -> list[str]:
        """Valida la configuración y retorna errores."""
        ...


# ============== Dependency Injection Contracts ==============

@runtime_checkable
class Container(ABC):
    """Contrato para contenedor de inyección de dependencias."""

    @abstractmethod
    def register(
        self,
        interface: type,
        implementation: type | Any,
        *,
        singleton: bool = True,
        **kwargs,
    ) -> None:
        """Registra una dependencia."""
        ...

    @abstractmethod
    def register_instance(
        self,
        interface: type,
        instance: Any,
    ) -> None:
        """Registra una instancia existente."""
        ...

    @abstractmethod
    def unregister(self, interface: type) -> bool:
        """Elimina una dependencia registrada."""
        ...

    @abstractmethod
    def resolve(self, interface: type) -> Any:
        """Resuelve una dependencia."""
        ...

    @abstractmethod
    def resolve_optional(self, interface: type, default: Any = None) -> Any:
        """Resuelve una dependencia opcional."""
        ...

    @abstractmethod
    def create_scope(self) -> Scope:
        """Crea un nuevo scope para dependencias."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Limpia todas las dependencias registradas."""
        ...


class Scope(ABC):
    """Scope para inyección de dependencias."""

    @abstractmethod
    def resolve(self, interface: type) -> Any:
        """Resuelve una dependencia en este scope."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Cierra el scope y limpia recursos."""
        ...


# ============== Kernel Contracts ==============

@runtime_checkable
class AIKernel(ABC):
    """Contrato para el kernel del AI Core."""

    @property
    @abstractmethod
    def config(self) -> AIConfiguration:
        """Obtiene la configuración del kernel."""
        ...

    @property
    @abstractmethod
    def model_registry(self) -> ModelRegistry:
        """Obtiene el registro de modelos."""
        ...

    @property
    @abstractmethod
    def container(self) -> Container:
        """Obtiene el contenedor de DI."""
        ...

    @abstractmethod
    async def initialize(self) -> None:
        """Inicializa el kernel y sus componentes."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Apaga el kernel limpiamente."""
        ...

    @abstractmethod
    async def process(self, request: AIRequest) -> AIResponse:
        """Procesa una request de IA."""
        ...

    @abstractmethod
    async def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        """Procesa una request de IA en streaming."""
        ...

    @abstractmethod
    async def health_check(self) -> HealthReport:
        """Verifica la salud del kernel."""
        ...


# ============== Context Contracts ==============

@runtime_checkable
class AIContextManager(ABC):
    """Contrato para gestión de contexto."""

    @abstractmethod
    def create_context(self, request: AIRequest) -> dict[str, Any]:
        """Crea un nuevo contexto para una request."""
        ...

    @abstractmethod
    def get_context(self, context_id: str) -> dict[str, Any] | None:
        """Obtiene un contexto existente."""
        ...

    @abstractmethod
    def update_context(self, context_id: str, updates: dict[str, Any]) -> None:
        """Actualiza un contexto existente."""
        ...

    @abstractmethod
    def delete_context(self, context_id: str) -> bool:
        """Elimina un contexto."""
        ...

    @abstractmethod
    def clear_all(self) -> None:
        """Limpia todos los contextos."""
        ...


# ============== Tool Contracts ==============

@runtime_checkable
class Tool(ABC):
    """Contrato para herramientas ejecutables."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre de la herramienta."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción de la herramienta."""
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """Schema de parámetros JSON."""
        ...

    @abstractmethod
    async def execute(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Ejecuta la herramienta."""
        ...


@runtime_checkable
class ToolRegistry(ABC):
    """Contrato para registro de herramientas."""

    @abstractmethod
    def register(self, tool: Tool) -> None:
        """Registra una nueva herramienta."""
        ...

    @abstractmethod
    def unregister(self, tool_name: str) -> bool:
        """Elimina una herramienta."""
        ...

    @abstractmethod
    def get(self, tool_name: str) -> Tool | None:
        """Obtiene una herramienta."""
        ...

    @abstractmethod
    def list_tools(self) -> list[Tool]:
        """Lista todas las herramientas."""
        ...

    @abstractmethod
    def get_definitions(self) -> list[ToolDefinition]:
        """Obtiene las definiciones de todas las herramientas."""
        ...
