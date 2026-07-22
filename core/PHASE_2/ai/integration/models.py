"""AI Core Models - Modelos del AI Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AICoreStatus(str, Enum):
    """Estados del AI Core."""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class ProcessingState(str, Enum):
    """Estados de procesamiento."""
    IDLE = "idle"
    BUILDING_CONTEXT = "building_context"
    RENDERING_PROMPT = "rendering_prompt"
    CALLING_PROVIDER = "calling_provider"
    EXECUTING_TOOLS = "executing_tools"
    COMPOSING_RESPONSE = "composing_response"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class AICoreConfig:
    """Configuración del AI Core."""
    # Providers
    default_provider: str = "openai"
    fallback_providers: list[str] = field(default_factory=list)
    
    # Límites
    max_tokens: int = 4096
    max_context_tokens: int = 128000
    
    # Features
    enable_memory: bool = True
    enable_tools: bool = True
    enable_streaming: bool = True
    
    # Sesiones
    session_timeout_minutes: int = 30
    default_token_budget: int = 100000
    
    # Prompt
    default_strategy: str = "direct"
    default_temperature: float = 0.7


@dataclass
class ProcessingContext:
    """Contexto de procesamiento."""
    request_id: str
    session_id: str | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    
    # Estado
    state: ProcessingState = ProcessingState.IDLE
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    
    # Resultado
    result: Any = None
    error: str | None = None
    
    # Metadatos
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AICoreMetrics:
    """Métricas del AI Core."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Tokens
    total_tokens_used: int = 0
    total_cost: float = 0.0
    
    # Tiempo
    avg_latency_ms: float = 0.0
    total_processing_time_ms: int = 0
    
    # Herramientas
    total_tool_calls: int = 0
    
    # Sesiones
    active_sessions: int = 0
    total_sessions: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests


@dataclass
class AICoreStats:
    """Estadísticas del AI Core."""
    status: AICoreStatus = AICoreStatus.INITIALIZING
    
    # Componentes
    memory_initialized: bool = False
    tools_initialized: bool = False
    providers_initialized: bool = False
    session_manager_initialized: bool = False
    
    # Métricas
    metrics: AICoreMetrics = field(default_factory=AICoreMetrics)
    
    # Tiempo
    started_at: datetime = field(default_factory=datetime.now)
    uptime_seconds: float = 0.0
    
    @property
    def is_ready(self) -> bool:
        return self.status == AICoreStatus.READY
    
    @property
    def all_components_ready(self) -> bool:
        return (
            self.memory_initialized and
            self.tools_initialized and
            self.providers_initialized and
            self.session_manager_initialized
        )
