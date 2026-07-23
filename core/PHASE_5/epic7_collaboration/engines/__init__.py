"""
PHASE 5 - EPIC 7: Collaboration Engines

Motores especializados para colaboración:
- ContextSharing
- AgentMessaging
- CollaborationBus
- SharedWorkspace
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM EPIC 7 DOMAIN
# =============================================================================

from core.PHASE_5.epic7_collaboration.domain import (
    SharedContext,
    ContextEntry,
    ContextType,
    CollaborationSession,
    SessionStatus,
    Participant,
    AgentConversation,
    Message,
    MessageType,
)


# =============================================================================
# SHARING RESULT
# =============================================================================

@dataclass
class SharingResult:
    """Resultado de compartición."""
    source_agent_id: str
    context_id: str
    
    # Resultado
    success: bool = True
    entries_shared: int = 0
    
    # Metadatos
    shared_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# MESSAGE RESULT
# =============================================================================

@dataclass
class MessageResult:
    """Resultado de envío de mensaje."""
    sender_id: str
    recipient_id: str
    
    # Resultado
    success: bool = True
    message_id: str = ""
    
    # Metadatos
    sent_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# BUS MESSAGE
# =============================================================================

@dataclass
class BusMessage:
    """Mensaje en el bus."""
    message_id: str = ""
    topic: str = ""
    sender_id: str = ""
    content: Any = None
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    priority: int = 5
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())


# =============================================================================
# WORKSPACE RESULT
# =============================================================================

@dataclass
class WorkspaceResult:
    """Resultado de operación en workspace."""
    workspace_id: str
    
    # Resultado
    success: bool = True
    artifacts: list[dict] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# CONTEXT SHARING
# =============================================================================

class ContextSharing:
    """
    Motor de compartición de contexto.
    
    Responsabilidades:
    - Compartir contexto entre agentes
    - Sincronizar estado
    - Gestionar TTL de entradas
    """
    
    def __init__(self):
        self._contexts: dict[str, SharedContext] = {}
    
    async def share_context(
        self,
        session_id: str,
        source_agent_id: str,
        entries: list[tuple[str, Any, ContextType]],
    ) -> SharingResult:
        """
        Comparte contexto con otros agentes.
        
        Args:
            session_id: ID de sesión
            source_agent_id: ID del agente fuente
            entries: Lista de (key, value, type)
        
        Returns:
            SharingResult con el resultado
        """
        logger.info(f"Sharing context from {source_agent_id} in session {session_id}")
        
        # Obtener o crear contexto
        if session_id not in self._contexts:
            self._contexts[session_id] = SharedContext(session_id=session_id)
        
        context = self._contexts[session_id]
        
        # Agregar entradas
        for key, value, context_type in entries:
            entry = ContextEntry(
                context_type=context_type,
                key=key,
                value=value,
                source_agent_id=source_agent_id,
            )
            context.add_entry(entry)
        
        return SharingResult(
            source_agent_id=source_agent_id,
            context_id=context.context_id,
            entries_shared=len(entries),
        )
    
    async def get_context(
        self,
        session_id: str,
        key: str | None = None,
        context_type: ContextType | None = None,
    ) -> SharedContext | None:
        """
        Obtiene contexto compartido.
        
        Args:
            session_id: ID de sesión
            key: Clave opcional
            context_type: Tipo opcional
        
        Returns:
            SharedContext o None
        """
        if session_id not in self._contexts:
            return None
        
        context = self._contexts[session_id]
        context.cleanup_expired()
        
        return context
    
    async def subscribe_to_context(
        self,
        session_id: str,
        agent_id: str,
    ) -> bool:
        """
        Suscribe un agente a actualizaciones de contexto.
        
        Args:
            session_id: ID de sesión
            agent_id: ID del agente
        
        Returns:
            True si exitoso
        """
        logger.info(f"Subscribing {agent_id} to context in session {session_id}")
        return True


# =============================================================================
# AGENT MESSAGING
# =============================================================================

class AgentMessaging:
    """
    Motor de mensajería entre agentes.
    
    Responsabilidades:
    - Enviar mensajes directos
    - Gestionar conversaciones
    - Notificar a agentes
    """
    
    def __init__(self):
        self._conversations: dict[str, AgentConversation] = {}
        self._message_queues: dict[str, list[Message]] = {}
    
    async def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        message_type: MessageType = MessageType.REQUEST,
        payload: dict | None = None,
    ) -> MessageResult:
        """
        Envía un mensaje a otro agente.
        
        Args:
            sender_id: ID del remitente
            recipient_id: ID del destinatario
            content: Contenido del mensaje
            message_type: Tipo de mensaje
            payload: Datos adicionales
        
        Returns:
            MessageResult con el resultado
        """
        logger.info(f"Sending message from {sender_id} to {recipient_id}")
        
        # Crear mensaje
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            payload=payload or {},
        )
        
        # Agregar a cola del destinatario
        if recipient_id not in self._message_queues:
            self._message_queues[recipient_id] = []
        self._message_queues[recipient_id].append(message)
        
        return MessageResult(
            sender_id=sender_id,
            recipient_id=recipient_id,
            success=True,
            message_id=message.message_id,
        )
    
    async def get_messages(
        self,
        agent_id: str,
        unread_only: bool = False,
    ) -> list[Message]:
        """
        Obtiene mensajes para un agente.
        
        Args:
            agent_id: ID del agente
            unread_only: Solo no leídos
        
        Returns:
            Lista de mensajes
        """
        if agent_id not in self._message_queues:
            return []
        
        messages = self._message_queues[agent_id]
        if unread_only:
            messages = [m for m in messages if not m.read]
        
        return messages
    
    async def mark_as_read(
        self,
        agent_id: str,
        message_ids: list[str],
    ) -> int:
        """
        Marca mensajes como leídos.
        
        Args:
            agent_id: ID del agente
            message_ids: IDs de mensajes
        
        Returns:
            Número de mensajes marcados
        """
        count = 0
        for message in self._message_queues.get(agent_id, []):
            if message.message_id in message_ids:
                message.mark_read()
                count += 1
        return count
    
    async def create_conversation(
        self,
        participants: list[str],
    ) -> AgentConversation:
        """
        Crea una conversación.
        
        Args:
            participants: Lista de IDs de agentes
        
        Returns:
            AgentConversation creada
        """
        conversation = AgentConversation(participants=participants)
        self._conversations[conversation.conversation_id] = conversation
        return conversation


# =============================================================================
# COLLABORATION BUS
# =============================================================================

class CollaborationBus:
    """
    Bus de colaboración.
    
    Responsabilidades:
    - Publicar eventos
    - Suscribir a topics
    - Notificar a suscriptores
    """
    
    def __init__(self):
        self._subscriptions: dict[str, list[str]] = {}  # topic -> agent_ids
        self._messages: list[BusMessage] = []
    
    async def publish(
        self,
        topic: str,
        sender_id: str,
        content: Any,
        priority: int = 5,
    ) -> BusMessage:
        """
        Publica un mensaje en el bus.
        
        Args:
            topic: Topic
            sender_id: ID del remitente
            content: Contenido
            priority: Prioridad
        
        Returns:
            BusMessage publicado
        """
        logger.info(f"Publishing to topic {topic} from {sender_id}")
        
        message = BusMessage(
            topic=topic,
            sender_id=sender_id,
            content=content,
            priority=priority,
        )
        
        self._messages.append(message)
        
        return message
    
    async def subscribe(
        self,
        agent_id: str,
        topic: str,
    ) -> bool:
        """
        Suscribe un agente a un topic.
        
        Args:
            agent_id: ID del agente
            topic: Topic
        
        Returns:
            True si exitoso
        """
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        
        if agent_id not in self._subscriptions[topic]:
            self._subscriptions[topic].append(agent_id)
        
        logger.info(f"Subscribed {agent_id} to topic {topic}")
        return True
    
    async def unsubscribe(
        self,
        agent_id: str,
        topic: str,
    ) -> bool:
        """
        Desuscribe un agente de un topic.
        
        Args:
            agent_id: ID del agente
            topic: Topic
        
        Returns:
            True si exitoso
        """
        if topic in self._subscriptions:
            if agent_id in self._subscriptions[topic]:
                self._subscriptions[topic].remove(agent_id)
        return True
    
    async def get_messages(
        self,
        agent_id: str,
        topic: str | None = None,
    ) -> list[BusMessage]:
        """
        Obtiene mensajes para un agente.
        
        Args:
            agent_id: ID del agente
            topic: Topic opcional
        
        Returns:
            Lista de mensajes
        """
        if topic:
            if agent_id not in self._subscriptions.get(topic, []):
                return []
            return [m for m in self._messages if m.topic == topic]
        else:
            # Obtener todos los topics suscritos
            subscribed_topics = [
                t for t, agents in self._subscriptions.items()
                if agent_id in agents
            ]
            return [m for m in self._messages if m.topic in subscribed_topics]


# =============================================================================
# SHARED WORKSPACE
# =============================================================================

class SharedWorkspace:
    """
    Workspace compartido entre agentes.
    
    Responsabilidades:
    - Gestionar artefactos compartidos
    - Versionar cambios
    - Coordinar acceso
    """
    
    def __init__(self):
        self._workspaces: dict[str, dict] = {}
        self._artifacts: dict[str, list[dict]] = {}
    
    async def create_workspace(
        self,
        workspace_id: str,
        owner_id: str,
        description: str = "",
    ) -> dict:
        """
        Crea un workspace compartido.
        
        Args:
            workspace_id: ID del workspace
            owner_id: ID del propietario
        
        Returns:
            Workspace creado
        """
        workspace = {
            "workspace_id": workspace_id,
            "owner_id": owner_id,
            "description": description,
            "created_at": datetime.now(UTC).isoformat(),
            "members": [owner_id],
        }
        
        self._workspaces[workspace_id] = workspace
        self._artifacts[workspace_id] = []
        
        return workspace
    
    async def add_artifact(
        self,
        workspace_id: str,
        agent_id: str,
        artifact: dict,
    ) -> bool:
        """
        Agrega un artefacto al workspace.
        
        Args:
            workspace_id: ID del workspace
            agent_id: ID del agente
            artifact: Artefacto
        
        Returns:
            True si exitoso
        """
        if workspace_id not in self._workspaces:
            return False
        
        artifact_with_metadata = {
            **artifact,
            "created_by": agent_id,
            "created_at": datetime.now(UTC).isoformat(),
        }
        
        self._artifacts[workspace_id].append(artifact_with_metadata)
        return True
    
    async def get_artifacts(
        self,
        workspace_id: str,
    ) -> list[dict]:
        """
        Obtiene artefactos de un workspace.
        
        Args:
            workspace_id: ID del workspace
        
        Returns:
            Lista de artefactos
        """
        return self._artifacts.get(workspace_id, [])


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Result classes
    "SharingResult",
    "MessageResult",
    "BusMessage",
    "WorkspaceResult",
    # Engines
    "ContextSharing",
    "AgentMessaging",
    "CollaborationBus",
    "SharedWorkspace",
]
