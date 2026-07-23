"""
PHASE 5 - EPIC 7: Collaboration Engine

Motor de colaboración entre agentes.
Gestiona colaboración, intercambio de contexto y sincronización.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM PHASE 5 FOUNDATION
# =============================================================================

from core.PHASE_5.foundation import (
    BaseAgent,
    AgentType,
    AgentState,
)
from core.PHASE_5.foundation.domain import AgentTask, AgentResult

# =============================================================================
# IMPORTS FROM EPIC 7 DOMAIN
# =============================================================================

from core.PHASE_5.epic7_collaboration.domain import (
    SharedContext,
    ContextType,
    CollaborationSession,
    SessionStatus,
    Participant,
    AgentConversation,
    Message,
    MessageType,
)

# =============================================================================
# IMPORTS FROM EPIC 7 ENGINES
# =============================================================================

from core.PHASE_5.epic7_collaboration.engines import (
    ContextSharing,
    AgentMessaging,
    CollaborationBus,
    SharedWorkspace,
)


# =============================================================================
# COLLABORATION ENGINE CONFIG
# =============================================================================

@dataclass
class CollaborationEngineConfig:
    """Configuración del Collaboration Engine."""
    # Engines
    enable_context_sharing: bool = True
    enable_agent_messaging: bool = True
    enable_collaboration_bus: bool = True
    enable_shared_workspace: bool = True
    
    # Comportamiento
    default_context_ttl_seconds: int = 3600
    max_participants_per_session: int = 10
    
    # Topics del bus
    default_topics: list[str] = field(default_factory=lambda: [
        "task.completed",
        "task.failed",
        "agent.joined",
        "agent.left",
        "context.updated",
    ])


# =============================================================================
# COLLABORATION ENGINE
# =============================================================================

class CollaborationEngine(BaseAgent):
    """
    Motor de colaboración entre agentes.
    
    Responsabilidades:
    - Gestionar sesiones de colaboración
    - Compartir contexto entre agentes
    - Facilitar mensajería
    - Coordinar workspaces compartidos
    
    Hereda de BaseAgent para integrarse con el sistema de agentes.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: CollaborationEngineConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COLLABORATION,
            name="Collaboration Engine",
            description="Motor de colaboración entre agentes",
        )
        
        self.config = config or CollaborationEngineConfig()
        
        # Inicializar motores
        self._context_sharing = ContextSharing() if self.config.enable_context_sharing else None
        self._agent_messaging = AgentMessaging() if self.config.enable_agent_messaging else None
        self._collaboration_bus = CollaborationBus() if self.config.enable_collaboration_bus else None
        self._shared_workspace = SharedWorkspace() if self.config.enable_shared_workspace else None
        
        # Sesiones activas
        self._sessions: dict[str, CollaborationSession] = {}
        
        # Métricas
        self._sessions_created = 0
        self._messages_sent = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el motor."""
        await super().initialize()
        logger.info(f"CollaborationEngine {self.agent_id} initialized")
        
        # Suscribirse a topics por defecto
        if self._collaboration_bus and self.config.default_topics:
            for topic in self.config.default_topics:
                await self._collaboration_bus.subscribe(self.agent_id, topic)
    
    async def shutdown(self) -> None:
        """Detiene el motor."""
        await super().shutdown()
        logger.info(f"CollaborationEngine {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de colaboración."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Obtener parámetros
            input_data = task.input_data
            action = input_data.get("action", "session")
            
            # Procesar según acción
            if action == "session":
                result = await self._handle_session(input_data)
            elif action == "context":
                result = await self._handle_context(input_data)
            elif action == "message":
                result = await self._handle_message(input_data)
            elif action == "bus":
                result = await self._handle_bus(input_data)
            elif action == "workspace":
                result = await self._handle_workspace(input_data)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.95,
            )
            
        except Exception as e:
            logger.error(f"CollaborationEngine execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # SESSION HANDLERS
    # =============================================================================
    
    async def _handle_session(self, input_data: dict) -> dict:
        """Maneja operaciones de sesión."""
        operation = input_data.get("operation", "create")
        result = {"operation": operation}
        
        if operation == "create":
            session = await self.create_session(
                session_type=input_data.get("session_type", "parallel"),
                participants=input_data.get("participants", []),
            )
            result["session_id"] = session.session_id
            result["status"] = session.status.value
        
        elif operation == "start":
            session_id = input_data.get("session_id")
            if session_id in self._sessions:
                self._sessions[session_id].start()
                result["status"] = "active"
        
        elif operation == "complete":
            session_id = input_data.get("session_id")
            if session_id in self._sessions:
                self._sessions[session_id].complete()
                result["status"] = "completed"
        
        elif operation == "info":
            session_id = input_data.get("session_id")
            if session_id in self._sessions:
                session = self._sessions[session_id]
                result["session_id"] = session.session_id
                result["status"] = session.status.value
                result["participants_count"] = len(session.participants)
        
        return result
    
    async def create_session(
        self,
        session_type: str,
        participants: list[str],
    ) -> CollaborationSession:
        """Crea una nueva sesión de colaboración."""
        session = CollaborationSession(
            session_type=session_type,
            shared_context=SharedContext(session_id=""),
        )
        
        # Agregar participantes
        for agent_id in participants:
            session.add_participant(agent_id)
        
        self._sessions[session.session_id] = session
        self._sessions_created += 1
        
        logger.info(f"Created collaboration session: {session.session_id}")
        
        return session
    
    # =============================================================================
    # CONTEXT HANDLERS
    # =============================================================================
    
    async def _handle_context(self, input_data: dict) -> dict:
        """Maneja operaciones de contexto."""
        operation = input_data.get("operation", "share")
        result = {"operation": operation}
        
        if operation == "share":
            sharing_result = await self.share_context(
                session_id=input_data.get("session_id"),
                agent_id=input_data.get("agent_id"),
                entries=input_data.get("entries", []),
            )
            result["success"] = sharing_result.get("success", False)
            result["entries_shared"] = sharing_result.get("entries_shared", 0)
        
        elif operation == "get":
            context = await self.get_context(
                session_id=input_data.get("session_id"),
                key=input_data.get("key"),
            )
            if context:
                result["context_id"] = context.context_id
                result["entries_count"] = context.entries_count
        
        return result
    
    async def share_context(
        self,
        session_id: str,
        agent_id: str,
        entries: list[tuple[str, Any, str]],
    ) -> dict:
        """Comparte contexto con otros agentes."""
        if not self._context_sharing:
            return {"success": False, "entries_shared": 0}
        
        # Convertir tipos
        typed_entries = []
        for key, value, type_str in entries:
            try:
                context_type = ContextType(type_str)
                typed_entries.append((key, value, context_type))
            except ValueError:
                typed_entries.append((key, value, ContextType.TASK))
        
        sharing_result = await self._context_sharing.share_context(
            session_id=session_id,
            source_agent_id=agent_id,
            entries=typed_entries,
        )
        
        return {
            "success": sharing_result.success,
            "entries_shared": sharing_result.entries_shared,
        }
    
    async def get_context(
        self,
        session_id: str,
        key: str | None = None,
    ) -> SharedContext | None:
        """Obtiene contexto compartido."""
        if not self._context_sharing:
            return None
        
        return await self._context_sharing.get_context(session_id, key)
    
    # =============================================================================
    # MESSAGE HANDLERS
    # =============================================================================
    
    async def _handle_message(self, input_data: dict) -> dict:
        """Maneja operaciones de mensajería."""
        operation = input_data.get("operation", "send")
        result = {"operation": operation}
        
        if operation == "send":
            message_result = await self.send_message(
                sender_id=input_data.get("sender_id"),
                recipient_id=input_data.get("recipient_id"),
                content=input_data.get("content", ""),
                message_type=input_data.get("message_type", "request"),
            )
            result["success"] = message_result.get("success", False)
            result["message_id"] = message_result.get("message_id", "")
            self._messages_sent += 1
        
        elif operation == "receive":
            messages = await self.receive_messages(
                agent_id=input_data.get("agent_id"),
                unread_only=input_data.get("unread_only", False),
            )
            result["messages_count"] = len(messages)
        
        return result
    
    async def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        message_type: str = "request",
    ) -> dict:
        """Envía un mensaje a otro agente."""
        if not self._agent_messaging:
            return {"success": False}
        
        try:
            msg_type = MessageType(message_type)
        except ValueError:
            msg_type = MessageType.REQUEST
        
        message_result = await self._agent_messaging.send_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            message_type=msg_type,
        )
        
        return {
            "success": message_result.success,
            "message_id": message_result.message_id,
        }
    
    async def receive_messages(
        self,
        agent_id: str,
        unread_only: bool = False,
    ) -> list[Message]:
        """Recibe mensajes para un agente."""
        if not self._agent_messaging:
            return []
        
        return await self._agent_messaging.get_messages(agent_id, unread_only)
    
    # =============================================================================
    # BUS HANDLERS
    # =============================================================================
    
    async def _handle_bus(self, input_data: dict) -> dict:
        """Maneja operaciones del bus."""
        operation = input_data.get("operation", "publish")
        result = {"operation": operation}
        
        if operation == "publish":
            message = await self.publish_event(
                topic=input_data.get("topic"),
                sender_id=input_data.get("sender_id"),
                content=input_data.get("content"),
            )
            result["message_id"] = message.message_id
        
        elif operation == "subscribe":
            success = await self.subscribe_to_topic(
                agent_id=input_data.get("agent_id"),
                topic=input_data.get("topic"),
            )
            result["success"] = success
        
        return result
    
    async def publish_event(
        self,
        topic: str,
        sender_id: str,
        content: Any,
    ) -> dict:
        """Publica un evento en el bus."""
        if not self._collaboration_bus:
            return {"message_id": ""}
        
        message = await self._collaboration_bus.publish(
            topic=topic,
            sender_id=sender_id,
            content=content,
        )
        
        return {"message_id": message.message_id}
    
    async def subscribe_to_topic(
        self,
        agent_id: str,
        topic: str,
    ) -> bool:
        """Suscribe a un topic."""
        if not self._collaboration_bus:
            return False
        
        return await self._collaboration_bus.subscribe(agent_id, topic)
    
    # =============================================================================
    # WORKSPACE HANDLERS
    # =============================================================================
    
    async def _handle_workspace(self, input_data: dict) -> dict:
        """Maneja operaciones de workspace."""
        operation = input_data.get("operation", "create")
        result = {"operation": operation}
        
        if operation == "create":
            workspace = await self.create_workspace(
                workspace_id=input_data.get("workspace_id"),
                owner_id=input_data.get("owner_id"),
            )
            result["workspace_id"] = workspace["workspace_id"]
        
        elif operation == "add_artifact":
            success = await self.add_artifact(
                workspace_id=input_data.get("workspace_id"),
                agent_id=input_data.get("agent_id"),
                artifact=input_data.get("artifact", {}),
            )
            result["success"] = success
        
        return result
    
    async def create_workspace(
        self,
        workspace_id: str,
        owner_id: str,
    ) -> dict:
        """Crea un workspace compartido."""
        if not self._shared_workspace:
            return {}
        
        return await self._shared_workspace.create_workspace(
            workspace_id=workspace_id,
            owner_id=owner_id,
        )
    
    async def add_artifact(
        self,
        workspace_id: str,
        agent_id: str,
        artifact: dict,
    ) -> bool:
        """Agrega un artefacto al workspace."""
        if not self._shared_workspace:
            return False
        
        return await self._shared_workspace.add_artifact(
            workspace_id=workspace_id,
            agent_id=agent_id,
            artifact=artifact,
        )
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del motor."""
        return {
            "sessions_created": self._sessions_created,
            "active_sessions": len(self._sessions),
            "messages_sent": self._messages_sent,
            "engines_enabled": {
                "context_sharing": self._context_sharing is not None,
                "agent_messaging": self._agent_messaging is not None,
                "collaboration_bus": self._collaboration_bus is not None,
                "shared_workspace": self._shared_workspace is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CollaborationEngine",
    "CollaborationEngineConfig",
]
