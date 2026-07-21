"""AI Core Controller - Controlador principal del AI Core."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, AsyncIterator

from core.ai.conversation import ConversationController
from core.ai.context import ContextBuilder
from core.ai.memory import MemoryManager
from core.ai.prompt import PromptBuilder, PromptConfig
from core.ai.providers import (
    ProviderManager,
    OpenAIProvider,
    AnthropicProvider,
    ProviderConfig,
    ProviderType,
    ChatMessage,
)
from core.ai.response import (
    ResponseComposer,
    ResponseType,
    StreamChunk,
)
from core.ai.sessions import SessionManager, Session, ConversationLimit
from core.ai.tools import ToolOrchestrator, ToolDefinition

from core.ai.integration.models import (
    AICoreConfig,
    AICoreMetrics,
    AICoreStats,
    AICoreStatus,
    ProcessingContext,
    ProcessingState,
)
from core.ai.integration import setup_integration


class AICoreController:
    """
    Controlador principal del AI Core.
    
    Integra todos los componentes:
    - Conversation Controller
    - Memory Manager
    - Prompt Builder
    - Context Builder
    - Tool Orchestrator
    - Provider Layer
    - Response Composer
    - Session Manager
    """

    def __init__(self, config: AICoreConfig | None = None) -> None:
        self._config = config or AICoreConfig()
        self._status = AICoreStatus.INITIALIZING
        
        # Componentes
        self._conversation: ConversationController | None = None
        self._memory: MemoryManager | None = None
        self._prompt: PromptBuilder | None = None
        self._context: ContextBuilder | None = None
        self._tools: ToolOrchestrator | None = None
        self._providers: ProviderManager | None = None
        self._sessions: SessionManager | None = None
        
        # Integration components (EPIC 11)
        self._gateways: dict[str, object] = {}
        self._memory_bridge = None
        self._event_bridge = None
        
        # Métricas
        self._metrics = AICoreMetrics()
        
        # Estado
        self._started_at = datetime.now()

    @property
    def status(self) -> AICoreStatus:
        return self._status
    
    @property
    def stats(self) -> AICoreStats:
        """Obtiene estadísticas del AI Core."""
        uptime = (datetime.now() - self._started_at).total_seconds()
        
        return AICoreStats(
            status=self._status,
            memory_initialized=self._memory is not None,
            tools_initialized=self._tools is not None,
            providers_initialized=self._providers is not None,
            session_manager_initialized=self._sessions is not None,
            metrics=self._metrics,
            started_at=self._started_at,
            uptime_seconds=uptime,
        )

    async def initialize(self) -> None:
        """Inicializa todos los componentes."""
        try:
            # ============================================
            # EPIC 11: Setup Integration Layer
            # ============================================
            integration = setup_integration(
                uow_factory=None,  # Uses default
                event_bus=None,     # Uses default
            )
            self._gateways = integration["gateways"]
            self._memory_bridge = integration["memory_bridge"]
            self._event_bridge = integration["event_bridge"]
            
            # Inicializar Session Manager
            self._sessions = SessionManager(
                default_budget=self._config.default_token_budget,
                default_limits=ConversationLimit(
                    max_messages_per_session=100,
                    session_timeout_minutes=self._config.session_timeout_minutes,
                ),
            )
            
            # Inicializar Providers
            self._providers = ProviderManager()
            
            openai_config = ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="gpt-4",
                max_tokens=self._config.max_tokens,
                temperature=self._config.default_temperature,
            )
            self._providers.register_provider(
                OpenAIProvider(),
                openai_config,
            )
            
            anthropic_config = ProviderConfig(
                provider_type=ProviderType.ANTHROPIC,
                model="claude-3-sonnet",
                max_tokens=self._config.max_tokens,
                temperature=self._config.default_temperature,
            )
            self._providers.register_provider(
                AnthropicProvider(),
                anthropic_config,
            )
            
            # Inicializar Memory
            if self._config.enable_memory:
                self._memory = MemoryManager()
            
            # Inicializar Tools
            if self._config.enable_tools:
                self._tools = ToolOrchestrator()
            
            # Inicializar Context Builder with injected gateways (EPIC 11)
            from core.ai.context_builder.providers import get_providers_with_gateways
            providers = get_providers_with_gateways(
                device_gateway=self._gateways.get("device"),
                incident_gateway=self._gateways.get("incident"),
                knowledge_gateway=self._gateways.get("knowledge"),
                recommendation_gateway=self._gateways.get("recommendation"),
                hospital_gateway=self._gateways.get("hospital"),
            )
            self._context = ContextBuilder(providers=providers)
            
            # Inicializar Prompt Builder
            self._prompt = PromptBuilder(PromptConfig(
                strategy=self._config.default_strategy,
            ))
            
            # Inicializar Conversation Controller
            self._conversation = ConversationController()
            
            self._status = AICoreStatus.READY
        
        except Exception as e:
            self._status = AICoreStatus.ERROR
            raise

    async def process(
        self,
        user_input: str,
        session_id: str | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> tuple[str, ProcessingContext]:
        """
        Procesa una solicitud del usuario.
        
        Returns:
            Tupla (respuesta, contexto de procesamiento)
        """
        request_id = str(uuid.uuid4())
        processing = ProcessingContext(
            request_id=request_id,
            session_id=session_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )
        
        self._status = AICoreStatus.PROCESSING
        self._metrics.total_requests += 1
        
        try:
            # 1. Obtener o crear sesión
            session = self._get_or_create_session(
                session_id, user_id, tenant_id
            )
            processing.session_id = session.id
            
            # 2. Agregar mensaje del usuario
            if self._sessions:
                self._sessions.add_message(
                    session.id, "user", user_input
                )
            
            processing.state = ProcessingState.BUILDING_CONTEXT
            
            # 3. Construir contexto
            context_data = await self._build_context(
                user_input, session, context
            )
            
            # 4. Construir prompt
            processing.state = ProcessingState.RENDERING_PROMPT
            prompt_config = PromptConfig(strategy=self._config.default_strategy)
            prompt = await self._prompt.build(
                user_input, context_data, config=prompt_config
            )
            
            # 5. Llamar al provider
            processing.state = ProcessingState.CALLING_PROVIDER
            messages = [
                ChatMessage(role="system", content=prompt),
                ChatMessage(role="user", content=user_input),
            ]
            
            result = await self._providers.chat_complete(messages)
            
            if not result.success:
                raise Exception(result.error)
            
            # 6. Componer respuesta
            processing.state = ProcessingState.COMPOSING_RESPONSE
            composer = ResponseComposer()
            composer.create_response(ResponseType.MARKDOWN)
            composer.add_text(result.message.content)
            response = composer.complete()
            
            # 7. Agregar respuesta a sesión
            if self._sessions:
                self._sessions.add_message(
                    session.id, "assistant", result.message.content
                )
            
            # 8. Actualizar memoria
            if self._memory:
                await self._memory.store(
                    user_input, result.message.content, session.id
                )
            
            # 9. Actualizar métricas
            self._metrics.successful_requests += 1
            self._metrics.total_tokens_used += result.usage.total_tokens
            
            processing.state = ProcessingState.COMPLETE
            processing.completed_at = datetime.now()
            processing.result = response.to_markdown()
            
            self._status = AICoreStatus.READY
            return response.to_markdown(), processing
        
        except Exception as e:
            processing.state = ProcessingState.FAILED
            processing.error = str(e)
            processing.completed_at = datetime.now()
            
            self._metrics.failed_requests += 1
            self._status = AICoreStatus.ERROR
            
            return f"Error: {str(e)}", processing

    async def process_stream(
        self,
        user_input: str,
        session_id: str | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Procesa con streaming."""
        response_text = ""
        
        # Primero procesar normal
        response, _ = await self.process(
            user_input, session_id, user_id, tenant_id, context
        )
        
        # Luego hacer streaming del resultado
        for i, char in enumerate(response):
            response_text += char
            yield StreamChunk(
                content=char,
                delta=char,
                is_final=i == len(response) - 1,
            )

    async def _build_context(
        self,
        user_input: str,
        session: Session,
        extra_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Construye el contexto de procesamiento."""
        context_data = {}
        
        # Agregar contexto de sesión
        if session.context:
            context_data["session"] = {
                "topic": session.context.topic,
                "domain": session.context.domain,
            }
        
        # Agregar historial de memoria
        if self._memory:
            memories = await self._memory.retrieve(user_input, limit=5)
            context_data["memories"] = [m.content for m in memories]
        
        # Agregar herramientas disponibles
        if self._tools:
            tools = self._tools.list_tools()
            context_data["tools"] = [
                {"id": t.id, "name": t.name} for t in tools
            ]
        
        # Agregar contexto extra
        if extra_context:
            context_data.update(extra_context)
        
        return context_data

    def _get_or_create_session(
        self,
        session_id: str | None,
        user_id: str | None,
        tenant_id: str | None,
    ) -> Session:
        """Obtiene o crea una sesión."""
        if session_id and self._sessions:
            session = self._sessions.get_session(session_id)
            if session:
                return session
        
        if self._sessions and user_id:
            session = self._sessions.create_session(
                user_id=user_id,
                tenant_id=tenant_id,
            )
            return session
        
        # Crear sesión temporal
        return Session(
            id=str(uuid.uuid4()),
            user_id=user_id or "anonymous",
            tenant_id=tenant_id,
        )

    async def shutdown(self) -> None:
        """Apaga el AI Core."""
        self._status = AICoreStatus.SHUTDOWN
        
        # Limpiar recursos
        self._sessions = None
        self._memory = None
        self._tools = None
        self._providers = None
        
        self._status = AICoreStatus.SHUTDOWN
