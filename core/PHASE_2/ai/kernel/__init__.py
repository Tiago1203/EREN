"""AI Kernel - Núcleo central del AI Core."""

from __future__ import annotations

import logging
import uuid
from typing import Any, AsyncIterator

from core.PHASE_2.ai.config import DictAIConfiguration
from core.PHASE_2.ai.contracts import (
    AIConfiguration,
    AIContextManager as AIContextManagerContract,
    AIKernel as AIKernelContract,
    Container,
)
from core.PHASE_2.ai.context import AIContextManager
from core.PHASE_2.ai.di import ContainerImpl, get_container
from core.PHASE_2.ai.dto import (
    AIContext,
    AIRequest,
    AIResponse,
    HealthReport,
    HealthStatus,
    ModelInfo,
    StreamChunk,
)
from core.PHASE_2.ai.exceptions import AIInitializationError, AIProcessingError
from core.PHASE_2.ai.providers import ProviderRouter
from core.PHASE_2.ai.registry import ModelRegistry

logger = logging.getLogger(__name__)


class AIKernel(AIKernelContract):
    """
    Kernel central del AI Core.
    
    Coordina todos los componentes del AI Core y provee
    la interfaz principal para procesamiento de requests.
    """

    def __init__(
        self,
        config: AIConfiguration | None = None,
        container: Container | None = None,
    ) -> None:
        """
        Inicializa el kernel.
        
        Args:
            config: Configuración del AI Core
            container: Contenedor de DI
        """
        self._config = config or DictAIConfiguration()
        self._container = container or get_container()
        self._initialized = False

        # Initialize components
        self._model_registry = ModelRegistry(
            default_model=self._config.get("default_model", "gpt-4")
        )
        self._provider_router = ProviderRouter()
        self._context_manager = AIContextManager()

        # Register core components in container
        self._register_components()

    def _register_components(self) -> None:
        """Registra los componentes core en el contenedor de DI."""
        # Only register if using the default container
        if isinstance(self._container, ContainerImpl):
            self._container.register_instance(
                AIConfiguration,
                self._config,
            )
            self._container.register_instance(
                ModelRegistry,
                self._model_registry,
            )
            self._container.register_instance(
                Container,
                self._container,
            )
            self._container.register_instance(
                AIContextManagerContract,
                self._context_manager,
            )

    @property
    def config(self) -> AIConfiguration:
        """Obtiene la configuración del kernel."""
        return self._config

    @property
    def model_registry(self) -> ModelRegistry:
        """Obtiene el registro de modelos."""
        return self._model_registry

    @property
    def container(self) -> Container:
        """Obtiene el contenedor de DI."""
        return self._container

    async def initialize(self) -> None:
        """
        Inicializa el kernel y sus componentes.
        
        Debe ser llamado antes de procesar cualquier request.
        """
        if self._initialized:
            logger.warning("AI Kernel already initialized")
            return

        logger.info("Initializing AI Kernel...")

        try:
            # Validate configuration
            errors = self._config.validate()
            if errors:
                logger.warning(f"Configuration warnings: {errors}")

            # Register default models
            await self._register_default_models()

            # Initialize providers
            await self._initialize_providers()

            self._initialized = True
            logger.info("AI Kernel initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AI Kernel: {e}")
            raise AIInitializationError(
                f"Kernel initialization failed: {e}",
                component="AIKernel",
            )

    async def _register_default_models(self) -> None:
        """Registra los modelos por defecto."""
        default_models = [
            ModelInfo(
                id="gpt-4",
                name="GPT-4",
                provider="openai",
                max_tokens=8192,
                supports_functions=True,
                supports_streaming=True,
                input_cost_per_1k=0.03,
                output_cost_per_1k=0.06,
            ),
            ModelInfo(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                provider="openai",
                max_tokens=128000,
                supports_functions=True,
                supports_vision=True,
                supports_streaming=True,
                input_cost_per_1k=0.01,
                output_cost_per_1k=0.03,
            ),
            ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider="openai",
                max_tokens=16385,
                supports_functions=True,
                supports_streaming=True,
                input_cost_per_1k=0.0005,
                output_cost_per_1k=0.0015,
            ),
            ModelInfo(
                id="claude-3-opus",
                name="Claude 3 Opus",
                provider="anthropic",
                max_tokens=200000,
                supports_functions=True,
                supports_vision=True,
                supports_streaming=True,
                input_cost_per_1k=0.015,
                output_cost_per_1k=0.075,
            ),
            ModelInfo(
                id="claude-3-sonnet",
                name="Claude 3 Sonnet",
                provider="anthropic",
                max_tokens=200000,
                supports_functions=True,
                supports_vision=True,
                supports_streaming=True,
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.015,
            ),
        ]

        for model in default_models:
            self._model_registry.register_model(model)

    async def _initialize_providers(self) -> None:
        """Inicializa los proveedores de IA."""
        from core.PHASE_2.ai.providers import (
            AnthropicProvider,
            AzureOpenAIProvider,
            OpenAIProvider,
        )

        # Register provider classes
        self._provider_router.register_provider(OpenAIProvider())
        self._provider_router.register_provider(AnthropicProvider())
        self._provider_router.register_provider(AzureOpenAIProvider())

    async def shutdown(self) -> None:
        """Apaga el kernel limpiamente."""
        logger.info("Shutting down AI Kernel...")

        self._initialized = False
        logger.info("AI Kernel shut down")

    async def process(self, request: AIRequest) -> AIResponse:
        """
        Procesa una request de IA.
        
        Args:
            request: Request de IA
            
        Returns:
            Response del AI Core
        """
        if not self._initialized:
            raise AIInitializationError("AI Kernel not initialized")

        request_id = str(uuid.uuid4())

        try:
            # Get provider for model
            provider = self._provider_router.get_provider_for_model(request.model)

            # Process request
            logger.debug(f"Processing request {request_id} with model {request.model}")
            response = await provider.generate(request)

            logger.debug(f"Request {request_id} completed")
            return response

        except Exception as e:
            logger.error(f"Request {request_id} failed: {e}")
            raise AIProcessingError(
                f"Request processing failed: {e}",
                request_id=request_id,
            )

    async def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        """
        Procesa una request de IA en streaming.
        
        Args:
            request: Request de IA
            
        Yields:
            Chunks de la respuesta
        """
        if not self._initialized:
            raise AIInitializationError("AI Kernel not initialized")

        request_id = str(uuid.uuid4())

        try:
            # Get provider for model
            provider = self._provider_router.get_provider_for_model(request.model)

            # Stream response
            logger.debug(f"Streaming request {request_id} with model {request.model}")

            async for chunk in provider.stream(request):
                yield chunk

            logger.debug(f"Request {request_id} stream completed")

        except Exception as e:
            logger.error(f"Request {request_id} stream failed: {e}")
            raise AIProcessingError(
                f"Stream processing failed: {e}",
                request_id=request_id,
            )

    async def health_check(self) -> HealthReport:
        """Verifica la salud del kernel."""
        components = []
        overall_status = "healthy"

        # Check model registry
        models = self._model_registry.list_models()
        if len(models) == 0:
            overall_status = "degraded"
            components.append(HealthStatus(
                component="model_registry",
                status="degraded",
                error="No models registered",
            ))
        else:
            components.append(HealthStatus(
                component="model_registry",
                status="healthy",
                metadata={"model_count": len(models)},
            ))

        # Check providers
        providers = self._provider_router.list_providers()
        if len(providers) == 0:
            overall_status = "unhealthy"
            components.append(HealthStatus(
                component="providers",
                status="unhealthy",
                error="No providers registered",
            ))
        else:
            components.append(HealthStatus(
                component="providers",
                status="healthy",
                metadata={"provider_count": len(providers)},
            ))

        # Check configuration
        config_errors = self._config.validate()
        if config_errors:
            overall_status = "degraded"
            components.append(HealthStatus(
                component="configuration",
                status="degraded",
                error="; ".join(config_errors),
            ))
        else:
            components.append(HealthStatus(
                component="configuration",
                status="healthy",
            ))

        return HealthReport(
            overall_status=overall_status,
            components=components,
        )

    def get_context_manager(self) -> AIContextManager:
        """Obtiene el gestor de contextos."""
        return self._context_manager


# ============== Global Kernel Instance ==============

_kernel: AIKernel | None = None


async def get_kernel() -> AIKernel:
    """Obtiene o crea el kernel global."""
    global _kernel
    if _kernel is None:
        _kernel = AIKernel()
        await _kernel.initialize()
    return _kernel


async def shutdown_kernel() -> None:
    """Apaga el kernel global."""
    global _kernel
    if _kernel is not None:
        await _kernel.shutdown()
        _kernel = None


def reset_kernel() -> None:
    """Resetea el kernel global."""
    _kernel = None
