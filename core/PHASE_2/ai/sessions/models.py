"""Session Models - Modelos de sesión."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class SessionStatus(str, Enum):
    """Estados de sesión."""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    CLOSED = "closed"


class SessionEvent(str, Enum):
    """Eventos de sesión."""
    CREATED = "created"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    RESUMED = "resumed"
    PAUSED = "paused"
    EXPIRED = "expired"
    CLOSED = "closed"


@dataclass
class TokenBudget:
    """Presupuesto de tokens para una sesión."""
    total_limit: int = 100000
    used_tokens: int = 0
    
    # Límites por período
    daily_limit: int = 50000
    daily_used: int = 0
    daily_reset_at: datetime | None = None
    
    # Alertas
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%
    
    @property
    def remaining(self) -> int:
        """Tokens restantes."""
        return max(0, self.total_limit - self.used_tokens)
    
    @property
    def daily_remaining(self) -> int:
        """Tokens diarios restantes."""
        return max(0, self.daily_limit - self.daily_used)
    
    @property
    def usage_percent(self) -> float:
        """Porcentaje de uso."""
        if self.total_limit == 0:
            return 0.0
        return self.used_tokens / self.total_limit
    
    @property
    def is_exhausted(self) -> bool:
        """Si el presupuesto está agotado."""
        return self.remaining <= 0 or self.daily_remaining <= 0
    
    @property
    def is_warning(self) -> bool:
        """Si está en nivel de advertencia."""
        return self.usage_percent >= self.warning_threshold
    
    @property
    def is_critical(self) -> bool:
        """Si está en nivel crítico."""
        return self.usage_percent >= self.critical_threshold
    
    def consume(self, tokens: int) -> bool:
        """
        Consume tokens del presupuesto.
        
        Returns:
            True si se pudieron consumir, False si no hay suficiente
        """
        if self.is_exhausted:
            return False
        
        self.used_tokens += tokens
        self.daily_used += tokens
        return True
    
    def reset_daily(self) -> None:
        """Resetea el contador diario."""
        self.daily_used = 0
        self.daily_reset_at = datetime.now()
    
    def check_daily_reset(self) -> None:
        """Verifica si necesita resetear el daily."""
        if self.daily_reset_at is None:
            self.reset_daily()
            return
        
        now = datetime.now()
        if now - self.daily_reset_at >= timedelta(days=1):
            self.reset_daily()


@dataclass
class Message:
    """Mensaje en la sesión."""
    id: str
    role: str  # user, assistant, system
    content: str
    
    # Tokens
    tokens: int = 0
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Contexto de la sesión."""
    session_id: str
    user_id: str
    tenant_id: str | None = None
    
    # Configuración
    max_messages: int = 100
    max_history: int = 50
    context_window: int = 10  # Mensajes recientes para contexto
    
    # Tema/dominio
    topic: str | None = None
    domain: str | None = None
    
    # Preferencias
    preferences: dict[str, Any] = field(default_factory=dict)
    
    # Metadatos
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationLimit:
    """Límites de conversación."""
    max_messages_per_session: int = 100
    max_message_length: int = 10000
    max_sessions_per_user: int = 10
    max_sessions_total: int = 1000
    
    # Tiempo
    session_timeout_minutes: int = 30
    inactivity_timeout_minutes: int = 15
    max_session_age_hours: int = 24
    
    # Tokens
    max_tokens_per_message: int = 4096
    max_context_tokens: int = 128000


@dataclass
class SessionEventRecord:
    """Registro de evento de sesión."""
    id: str
    session_id: str
    event_type: SessionEvent
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Detalles
    message_id: str | None = None
    tokens: int = 0
    duration_ms: int = 0
    
    # Metadatos
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Sesión de IA."""
    id: str
    user_id: str
    tenant_id: str | None = None
    
    # Estado
    status: SessionStatus = SessionStatus.ACTIVE
    
    # Contexto
    context: SessionContext | None = None
    
    # Mensajes
    messages: list[Message] = field(default_factory=list)
    
    # Budget
    token_budget: TokenBudget = field(default_factory=TokenBudget)
    
    # Límites
    limits: ConversationLimit = field(default_factory=ConversationLimit)
    
    # Tiempos
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_activity_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    
    # Eventos
    events: list[SessionEvent] = field(default_factory=list)
    
    # Metadatos
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Si la sesión está activa."""
        return self.status == SessionStatus.ACTIVE
    
    @property
    def is_expired(self) -> bool:
        """Si la sesión está expirada."""
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        if self.status == SessionStatus.EXPIRED:
            return True
        return False
    
    @property
    def message_count(self) -> int:
        """Cantidad de mensajes."""
        return len(self.messages)
    
    @property
    def total_tokens(self) -> int:
        """Total de tokens usados."""
        return sum(m.tokens for m in self.messages)
    
    @property
    def duration_minutes(self) -> float:
        """Duración en minutos."""
        delta = self.updated_at - self.created_at
        return delta.total_seconds() / 60
    
    def add_message(self, message: Message) -> bool:
        """
        Agrega un mensaje a la sesión.
        
        Returns:
            True si se agregó, False si se alcanzó el límite
        """
        if self.message_count >= self.limits.max_messages_per_session:
            return False
        
        if len(message.content) > self.limits.max_message_length:
            return False
        
        self.messages.append(message)
        self.last_activity_at = datetime.now()
        self.updated_at = datetime.now()
        return True
    
    def can_resume(self) -> bool:
        """Verifica si la sesión puede reanudarse."""
        if self.status == SessionStatus.CLOSED:
            return False
        
        if self.is_expired:
            return False
        
        # Verificar edad máxima
        max_age = timedelta(hours=self.limits.max_session_age_hours)
        if datetime.now() - self.created_at > max_age:
            return False
        
        return True
    
    def get_context_messages(self) -> list[Message]:
        """Obtiene los mensajes de contexto recientes."""
        return self.messages[-self.context.context_window:]
    
    def check_limits(self) -> tuple[bool, str]:
        """
        Verifica los límites de la sesión.
        
        Returns:
            Tupla (puede continuar, mensaje de error)
        """
        if self.token_budget.is_exhausted:
            return False, "Token budget exhausted"
        
        if self.message_count >= self.limits.max_messages_per_session:
            return False, "Maximum messages reached"
        
        if self.is_expired:
            return False, "Session expired"
        
        return True, ""
    
    def pause(self) -> None:
        """Pausa la sesión."""
        self.status = SessionStatus.IDLE
    
    def resume(self) -> bool:
        """Reanuda la sesión."""
        if not self.can_resume():
            return False
        
        self.status = SessionStatus.ACTIVE
        self.last_activity_at = datetime.now()
        return True
    
    def close(self) -> None:
        """Cierra la sesión."""
        self.status = SessionStatus.CLOSED
    
    def expire(self) -> None:
        """Marca la sesión como expirada."""
        self.status = SessionStatus.EXPIRED


@dataclass
class SessionStats:
    """Estadísticas de sesión."""
    session_id: str
    
    # Counts
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    
    # Tokens
    total_tokens: int = 0
    avg_tokens_per_message: float = 0.0
    
    # Tiempo
    total_duration_ms: int = 0
    avg_response_time_ms: float = 0.0
    
    # Actividad
    created_at: datetime = field(default_factory=datetime.now)
    last_activity_at: datetime = field(default_factory=datetime.now)
    
    # Budget
    initial_budget: int = 0
    final_budget: int = 0
    budget_usage_percent: float = 0.0
