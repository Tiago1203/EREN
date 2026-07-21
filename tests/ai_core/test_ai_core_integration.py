"""Tests de integración del AI Core.

Este módulo valida la integración completa de todos los componentes
del AI Core (EPIC 0-9).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestAICoreImports:
    """Test que todos los exports están disponibles."""

    def test_import_kernel(self):
        """Verifica que kernel está importable."""
        from core.ai import AIKernel
        assert AIKernel is not None

    def test_import_conversation(self):
        """Verifica que conversation está importable."""
        from core.ai import ConversationController
        assert ConversationController is not None

    def test_import_context_builder(self):
        """Verifica que context_builder está importable."""
        from core.ai import ContextBuilder
        assert ContextBuilder is not None

    def test_import_prompt(self):
        """Verifica que prompt está importable."""
        from core.ai import PromptBuilder
        assert PromptBuilder is not None

    def test_import_memory(self):
        """Verifica que memory está importable."""
        from core.ai import MemoryManager
        assert MemoryManager is not None

    def test_import_tools(self):
        """Verifica que tools está importable."""
        from core.ai import ToolOrchestrator
        assert ToolOrchestrator is not None

    def test_import_response(self):
        """Verifica que response está importable."""
        from core.ai import ResponseComposer
        assert ResponseComposer is not None

    def test_import_providers(self):
        """Verifica que providers está importable."""
        from core.ai import ProviderManager
        assert ProviderManager is not None

    def test_import_sessions(self):
        """Verifica que sessions está importable."""
        from core.ai import SessionManager
        assert SessionManager is not None

    def test_import_integration(self):
        """Verifica que integration está importable."""
        from core.ai import AICoreController, AICoreConfig
        assert AICoreController is not None
        assert AICoreConfig is not None


class TestAICoreConfig:
    """Test de configuración del AI Core."""

    def test_default_config(self):
        """Verifica configuración por defecto."""
        from core.ai import AICoreConfig
        
        config = AICoreConfig()
        
        assert config.default_provider == "openai"
        assert config.enable_memory is True
        assert config.enable_tools is True
        assert config.enable_streaming is True
        assert config.max_tokens == 4096

    def test_custom_config(self):
        """Verifica configuración personalizada."""
        from core.ai import AICoreConfig
        
        config = AICoreConfig(
            default_provider="anthropic",
            max_tokens=8192,
            enable_memory=False,
        )
        
        assert config.default_provider == "anthropic"
        assert config.max_tokens == 8192
        assert config.enable_memory is False


class TestAICoreController:
    """Test del AICoreController."""

    def test_controller_creation(self):
        """Verifica que el controller se crea."""
        from core.ai import AICoreController, AICoreConfig
        
        config = AICoreConfig()
        controller = AICoreController(config)
        
        assert controller is not None
        assert controller.stats is not None

    def test_controller_initial_status(self):
        """Verifica estado inicial del controller."""
        from core.ai import AICoreController, AICoreStatus
        
        controller = AICoreController()
        
        # Estado debe ser INITIALIZING o READY
        assert controller.status in [
            AICoreStatus.INITIALIZING,
            AICoreStatus.READY,
        ]

    def test_controller_stats(self):
        """Verifica estadísticas del controller."""
        from core.ai import AICoreController
        
        controller = AICoreController()
        stats = controller.stats
        
        assert stats.metrics.total_requests == 0
        assert stats.metrics.successful_requests == 0


class TestSessionManagement:
    """Test de gestión de sesiones."""

    def test_create_session(self):
        """Verifica creación de sesión."""
        from core.ai import SessionManager, TokenBudget, ConversationLimit
        
        manager = SessionManager()
        session = manager.create_session(user_id="test-user")
        
        assert session is not None
        assert session.user_id == "test-user"
        assert session.is_active is True

    def test_session_token_budget(self):
        """Verifica presupuesto de tokens."""
        from core.ai import TokenBudget
        
        budget = TokenBudget(total_limit=1000)
        
        assert budget.remaining == 1000
        assert budget.is_exhausted is False

    def test_session_limits(self):
        """Verifica límites de conversación."""
        from core.ai import ConversationLimit
        
        limits = ConversationLimit(
            max_messages_per_session=50,
            session_timeout_minutes=60,
        )
        
        assert limits.max_messages_per_session == 50
        assert limits.session_timeout_minutes == 60


class TestProviders:
    """Test de proveedores de IA."""

    def test_provider_manager_creation(self):
        """Verifica creación del manager."""
        from core.ai import ProviderManager
        
        manager = ProviderManager()
        assert manager is not None

    def test_provider_types(self):
        """Verifica tipos de proveedor."""
        from core.ai import ProviderType
        
        assert ProviderType.OPENAI is not None
        assert ProviderType.ANTHROPIC is not None
        assert ProviderType.GOOGLE is not None
        assert ProviderType.OLLAMA is not None


class TestResponseComposer:
    """Test del Response Composer."""

    def test_create_response(self):
        """Verifica creación de respuesta."""
        from core.ai import ResponseComposer, ResponseType
        
        composer = ResponseComposer()
        response = composer.create_response(ResponseType.MARKDOWN)
        
        assert response is not None
        assert response.response_type == ResponseType.MARKDOWN

    def test_add_text(self):
        """Verifica agregar texto."""
        from core.ai import ResponseComposer
        
        composer = ResponseComposer()
        composer.create_response()
        composer.add_text("Hola mundo")
        
        assert len(composer._response.elements) == 1

    def test_add_code(self):
        """Verifica agregar código."""
        from core.ai import ResponseComposer
        
        composer = ResponseComposer()
        composer.create_response()
        composer.add_code("python", "print('hello')")
        
        assert len(composer._response.elements) == 1


class TestMemoryManager:
    """Test del Memory Manager."""

    def test_memory_creation(self):
        """Verifica creación del manager."""
        from core.ai import MemoryManager
        
        manager = MemoryManager()
        assert manager is not None

    def test_memory_types(self):
        """Verifica tipos de memoria."""
        from core.ai import MemoryType
        
        assert MemoryType.WORKING is not None
        assert MemoryType.SHORT is not None
        assert MemoryType.LONG is not None


class TestToolOrchestrator:
    """Test del Tool Orchestrator."""

    def test_orchestrator_creation(self):
        """Verifica creación del orchestrator."""
        from core.ai import ToolOrchestrator
        
        orchestrator = ToolOrchestrator()
        assert orchestrator is not None

    def test_tool_categories(self):
        """Verifica categorías de herramientas."""
        from core.ai import ToolCategory
        
        assert ToolCategory.DATABASE is not None
        assert ToolCategory.API is not None
        assert ToolCategory.CODE is not None


class TestPromptBuilder:
    """Test del Prompt Builder."""

    def test_builder_creation(self):
        """Verifica creación del builder."""
        from core.ai import PromptBuilder, PromptConfig
        
        config = PromptConfig()
        builder = PromptBuilder(config)
        
        assert builder is not None

    def test_prompt_strategies(self):
        """Verifica estrategias de prompt."""
        from core.ai.prompt import PromptStrategyType
        
        assert PromptStrategyType.DIRECT is not None
        assert PromptStrategyType.CHAIN_OF_THOUGHT is not None
        assert PromptStrategyType.FEW_SHOT is not None
