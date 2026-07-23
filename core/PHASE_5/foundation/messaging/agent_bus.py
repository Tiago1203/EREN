"""
PHASE 5 - EPIC 0: Agent Bus

Sistema de mensajería para comunicación entre agentes.
Permite envío de mensajes punto a punto y broadcast.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Callable, Awaitable, Any
from collections import defaultdict
import logging
import uuid

logger = logging.getLogger(__name__)


# =============================================================================
# AGENT BUS CONFIG
# =============================================================================

@dataclass
class AgentBusConfig:
    """Configuración del Agent Bus."""
    enable_persistence: bool = False
    max_queue_size: int = 1000
    message_ttl_seconds: int = 300
    enable_routing: bool = True
    enable_subscription: bool = True


# =============================================================================
# BUS MESSAGE
# =============================================================================

@dataclass
class BusMessage:
    """Mensaje del bus."""
    message_id: str = ""
    sender: str = ""
    receiver: str = ""  # agent_id o "*" para broadcast
    topic: str | None = None  # Para pub/sub
    
    # Contenido
    action: str = ""
    payload: dict = field(default_factory=dict)
    
    # Correlación
    correlation_id: str | None = None
    
    # Estado
    delivered: bool = False
    read_at: datetime | None = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())


# =============================================================================
# BUS SUBSCRIPTION
# =============================================================================

@dataclass
class BusSubscription:
    """Suscripción a un topic."""
    subscription_id: str = ""
    agent_id: str = ""
    topic: str = ""
    
    handler: Callable[[BusMessage], Awaitable[Any]] | None = None
    
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.subscription_id:
            self.subscription_id = str(uuid.uuid4())


# =============================================================================
# AGENT BUS
# =============================================================================

class AgentBus:
    """
    Bus de mensajería para agentes.
    
    Responsabilidades:
    - Envío de mensajes punto a punto
    - Broadcast a múltiples agentes
    - Pub/Sub por topics
    - Suscripciones y manejo de mensajes
    
    Este componente resuelve el problema de comunicación entre agentes.
    """
    
    def __init__(self, config: AgentBusConfig | None = None):
        self.config = config or AgentBusConfig()
        
        # Cola de mensajes por receptor
        self._inbox: dict[str, list[BusMessage]] = defaultdict(list)
        
        # Suscripciones por topic
        self._subscriptions: dict[str, list[BusSubscription]] = defaultdict(list)
        
        # Registro de handlers por agente
        self._handlers: dict[str, Callable] = {}
        
        # Estadísticas
        self._stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "broadcasts_sent": 0,
            "subscriptions_created": 0,
        }
    
    # =========================================================================
    # ENVÍO DE MENSAJES
    # =========================================================================
    
    async def send(
        self,
        sender: str,
        receiver: str,
        action: str,
        payload: dict | None = None,
        correlation_id: str | None = None,
    ) -> BusMessage:
        """
        Envía un mensaje a un agente específico.
        
        Args:
            sender: ID del agente remitente
            receiver: ID del agente receptor
            action: Acción del mensaje
            payload: Datos del mensaje
            correlation_id: ID de correlación
        
        Returns:
            BusMessage creado
        """
        message = BusMessage(
            sender=sender,
            receiver=receiver,
            action=action,
            payload=payload or {},
            correlation_id=correlation_id,
        )
        
        # Entregar directamente si el receptor tiene handler
        if receiver in self._handlers:
            await self._deliver_to_handler(receiver, message)
        else:
            # Encolar en inbox
            self._inbox[receiver].append(message)
        
        self._stats["messages_sent"] += 1
        logger.info(f"Message sent from {sender} to {receiver}: {action}")
        
        return message
    
    async def broadcast(
        self,
        sender: str,
        action: str,
        payload: dict | None = None,
        exclude: list[str] | None = None,
    ) -> list[BusMessage]:
        """
        Envía un mensaje broadcast a todos los agentes.
        
        Args:
            sender: ID del agente remitente
            action: Acción del mensaje
            payload: Datos del mensaje
            exclude: Agentes a excluir
        
        Returns:
            Lista de mensajes enviados
        """
        messages = []
        exclude = exclude or []
        
        # Enviar a todos los agentes con inbox
        for receiver in self._inbox.keys():
            if receiver != sender and receiver not in exclude:
                message = await self.send(
                    sender=sender,
                    receiver=receiver,
                    action=action,
                    payload=payload,
                )
                messages.append(message)
        
        self._stats["broadcasts_sent"] += 1
        logger.info(f"Broadcast from {sender} to {len(messages)} agents: {action}")
        
        return messages
    
    # =========================================================================
    # PUB/SUB
    # =========================================================================
    
    async def subscribe(
        self,
        agent_id: str,
        topic: str,
        handler: Callable[[BusMessage], Awaitable[Any]],
    ) -> BusSubscription:
        """
        Suscribe un agente a un topic.
        
        Args:
            agent_id: ID del agente
            topic: Topic al que suscribirse
            handler: Función handler para mensajes
        
        Returns:
            Suscripción creada
        """
        subscription = BusSubscription(
            agent_id=agent_id,
            topic=topic,
            handler=handler,
        )
        
        self._subscriptions[topic].append(subscription)
        self._stats["subscriptions_created"] += 1
        
        logger.info(f"Agent {agent_id} subscribed to topic {topic}")
        
        return subscription
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Cancela una suscripción."""
        for topic, subs in self._subscriptions.items():
            self._subscriptions[topic] = [
                s for s in subs if s.subscription_id != subscription_id
            ]
        return True
    
    async def publish(
        self,
        publisher: str,
        topic: str,
        action: str,
        payload: dict | None = None,
    ) -> list[BusMessage]:
        """
        Publica un mensaje en un topic (Pub/Sub).
        
        Args:
            publisher: ID del publicador
            topic: Topic de publicación
            action: Acción del mensaje
            payload: Datos del mensaje
        
        Returns:
            Lista de mensajes entregados
        """
        messages = []
        
        # Enviar a todos los suscriptores del topic
        for subscription in self._subscriptions.get(topic, []):
            if subscription.agent_id != publisher:
                message = BusMessage(
                    sender=publisher,
                    receiver=subscription.agent_id,
                    topic=topic,
                    action=action,
                    payload=payload or {},
                )
                
                if subscription.handler:
                    await subscription.handler(message)
                    message.delivered = True
                
                messages.append(message)
                self._stats["messages_delivered"] += 1
        
        logger.info(f"Published to topic {topic}: {len(messages)} subscribers")
        
        return messages
    
    # =========================================================================
    # RECEPCIÓN DE MENSAJES
    # =========================================================================
    
    async def receive(self, agent_id: str) -> BusMessage | None:
        """
        Recibe el siguiente mensaje del inbox.
        
        Args:
            agent_id: ID del agente receptor
        
        Returns:
            Próximo mensaje o None
        """
        if self._inbox[agent_id]:
            message = self._inbox[agent_id].pop(0)
            message.read_at = datetime.now(UTC)
            self._stats["messages_delivered"] += 1
            return message
        return None
    
    async def peek(self, agent_id: str, count: int = 10) -> list[BusMessage]:
        """
        Mira los mensajes sin consumirlos.
        
        Args:
            agent_id: ID del agente
            count: Número de mensajes a ver
        
        Returns:
            Lista de mensajes
        """
        return self._inbox[agent_id][:count]
    
    def register_handler(self, agent_id: str, handler: Callable) -> None:
        """
        Registra un handler para un agente.
        
        Args:
            agent_id: ID del agente
            handler: Función handler
        """
        self._handlers[agent_id] = handler
        logger.info(f"Handler registered for agent {agent_id}")
    
    async def _deliver_to_handler(self, agent_id: str, message: BusMessage) -> None:
        """Entrega un mensaje directamente al handler."""
        if agent_id in self._handlers:
            try:
                await self._handlers[agent_id](message)
                message.delivered = True
                message.read_at = datetime.now(UTC)
                self._stats["messages_delivered"] += 1
            except Exception as e:
                logger.error(f"Error delivering to handler {agent_id}: {e}")
    
    # =========================================================================
    # UTILIDADES
    # =========================================================================
    
    def get_inbox_count(self, agent_id: str) -> int:
        """Obtiene el número de mensajes en el inbox."""
        return len(self._inbox[agent_id])
    
    def get_topics(self) -> list[str]:
        """Obtiene la lista de topics con suscriptores."""
        return list(self._subscriptions.keys())
    
    def get_subscription_count(self, topic: str) -> int:
        """Obtiene el número de suscriptores de un topic."""
        return len(self._subscriptions.get(topic, []))
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del bus."""
        return {
            **self._stats,
            "topics_count": len(self._subscriptions),
            "total_subscriptions": sum(len(s) for s in self._subscriptions.values()),
        }
    
    def clear(self) -> None:
        """Limpia el bus."""
        self._inbox.clear()
        self._subscriptions.clear()
        logger.info("AgentBus cleared")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AgentBusConfig",
    "BusMessage",
    "BusSubscription",
    "AgentBus",
]
