"""
PHASE 5 - EPIC 0: Messaging

Sistema de mensajería entre agentes.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional
import asyncio
import uuid

from core.PHASE_5.foundation.types import (
    MessageType,
    MessageError,
    AgentPriority,
)
from core.PHASE_5.foundation.domain import AgentMessage


# =============================================================================
# MESSAGE BROKER - Broker de mensajes
# =============================================================================

class MessageBroker:
    """Broker de mensajes para comunicación entre agentes."""
    
    def __init__(self, max_queue_size: int = 1000):
        # Colas por agente
        self._queues: dict[str, deque[AgentMessage]] = {}
        
        # Topics para Pub/Sub
        self._topics: dict[str, set[str]] = {}  # topic -> set of agent_ids
        
        # Dead Letter Queue
        self._dlq: deque[AgentMessage] = deque(maxlen=10000)
        
        # Cola de espera para send_and_wait
        self._pending_responses: dict[str, asyncio.Future] = {}
        
        # Config
        self._max_queue_size = max_queue_size
    
    async def send(self, message: AgentMessage) -> bool:
        """Envía un mensaje a un agente específico."""
        try:
            message.sent_at = datetime.now(UTC)
            
            receiver = message.receiver
            
            # Inicializar cola si no existe
            if receiver not in self._queues:
                self._queues[receiver] = deque(maxlen=self._max_queue_size)
            
            # Agregar a cola
            self._queues[receiver].append(message)
            
            return True
        except Exception:
            return False
    
    async def publish(self, topic: str, message: AgentMessage) -> bool:
        """Publica un mensaje a todos los subscribers de un topic."""
        try:
            message.sent_at = datetime.now(UTC)
            message.topic = topic
            
            # Obtener subscribers
            subscribers = self._topics.get(topic, set())
            
            for agent_id in subscribers:
                if agent_id not in self._queues:
                    self._queues[agent_id] = deque(maxlen=self._max_queue_size)
                self._queues[agent_id].append(message)
            
            return True
        except Exception:
            return False
    
    async def subscribe(
        self,
        agent_id: str,
        topics: list[str],
    ) -> bool:
        """Suscribe un agente a topics."""
        for topic in topics:
            if topic not in self._topics:
                self._topics[topic] = set()
            self._topics[topic].add(agent_id)
        return True
    
    async def unsubscribe(
        self,
        agent_id: str,
        topics: list[str],
    ) -> bool:
        """Desuscribe un agente de topics."""
        for topic in topics:
            if topic in self._topics:
                self._topics[topic].discard(agent_id)
        return True
    
    async def receive(
        self,
        agent_id: str,
        timeout: int = 30,
    ) -> Optional[AgentMessage]:
        """Recibe el siguiente mensaje de la cola de un agente."""
        if agent_id not in self._queues:
            return None
        
        queue = self._queues[agent_id]
        
        if not queue:
            return None
        
        # Pop mensaje de la cola
        message = queue.popleft()
        message.received_at = datetime.now(UTC)
        
        return message
    
    async def send_and_wait(
        self,
        message: AgentMessage,
        timeout: int = 30,
    ) -> Optional[AgentMessage]:
        """Envía un mensaje y espera respuesta."""
        correlation_id = message.message_id
        
        # Crear Future para esperar respuesta
        future = asyncio.get_event_loop().create_future()
        self._pending_responses[correlation_id] = future
        
        try:
            # Enviar mensaje
            await self.send(message)
            
            # Esperar respuesta
            try:
                response = await asyncio.wait_for(future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                return None
        finally:
            # Limpiar Future
            self._pending_responses.pop(correlation_id, None)
    
    async def respond(self, response: AgentMessage) -> bool:
        """Responde a un mensaje pendiente."""
        correlation_id = response.correlation_id or response.parent_id
        
        if not correlation_id:
            return False
        
        future = self._pending_responses.get(correlation_id)
        if future and not future.done():
            future.set_result(response)
            return True
        
        return False
    
    async def get_queue_size(self, agent_id: str) -> int:
        """Obtiene tamaño de cola de un agente."""
        if agent_id not in self._queues:
            return 0
        return len(self._queues[agent_id])
    
    async def get_dlq(self) -> list[AgentMessage]:
        """Obtiene mensajes de la Dead Letter Queue."""
        return list(self._dlq)
    
    def add_to_dlq(self, message: AgentMessage) -> None:
        """Agrega mensaje a la Dead Letter Queue."""
        self._dlq.append(message)
    
    def get_subscribed_topics(self, agent_id: str) -> list[str]:
        """Obtiene topics a los que está suscrito un agente."""
        topics = []
        for topic, subscribers in self._topics.items():
            if agent_id in subscribers:
                topics.append(topic)
        return topics


# =============================================================================
# MESSAGE BUILDER - Builder para crear mensajes
# =============================================================================

class MessageBuilder:
    """Builder para crear mensajes entre agentes."""
    
    def __init__(self, sender: str):
        self._sender = sender
        self._receiver: str | None = None
        self._type: MessageType = MessageType.REQUEST
        self._action: str = ""
        self._payload: dict = {}
        self._priority: AgentPriority = AgentPriority.MEDIUM
        self._ttl: int = 300
        self._correlation_id: str | None = None
        self._topic: str | None = None
    
    def to(self, receiver: str) -> "MessageBuilder":
        """Establece receptor."""
        self._receiver = receiver
        return self
    
    def topic(self, topic: str) -> "MessageBuilder":
        """Establece topic para Pub/Sub."""
        self._topic = topic
        return self
    
    def request(self, action: str, payload: dict | None = None) -> "MessageBuilder":
        """Mensaje tipo REQUEST."""
        self._type = MessageType.REQUEST
        self._action = action
        self._payload = payload or {}
        return self
    
    def response(self, action: str, payload: dict | None = None) -> "MessageBuilder":
        """Mensaje tipo RESPONSE."""
        self._type = MessageType.RESPONSE
        self._action = action
        self._payload = payload or {}
        return self
    
    def notification(self, action: str, payload: dict | None = None) -> "MessageBuilder":
        """Mensaje tipo NOTIFICATION."""
        self._type = MessageType.NOTIFICATION
        self._action = action
        self._payload = payload or {}
        return self
    
    def event(self, action: str, payload: dict | None = None) -> "MessageBuilder":
        """Mensaje tipo EVENT."""
        self._type = MessageType.EVENT
        self._action = action
        self._payload = payload or {}
        return self
    
    def error(self, action: str, error: str) -> "MessageBuilder":
        """Mensaje tipo ERROR."""
        self._type = MessageType.ERROR
        self._action = action
        self._payload = {"error": error}
        return self
    
    def with_priority(self, priority: AgentPriority) -> "MessageBuilder":
        """Establece prioridad."""
        self._priority = priority
        return self
    
    def with_ttl(self, ttl: int) -> "MessageBuilder":
        """Establece TTL."""
        self._ttl = ttl
        return self
    
    def with_correlation(self, correlation_id: str) -> "MessageBuilder":
        """Establece correlation ID."""
        self._correlation_id = correlation_id
        return self
    
    def build(self) -> AgentMessage:
        """Construye el mensaje."""
        if not self._receiver:
            raise ValueError("Receiver is required")
        
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            sender=self._sender,
            receiver=self._receiver,
            type=self._type,
            action=self._action,
            payload=self._payload,
            topic=self._topic,
            priority=self._priority,
            ttl=self._ttl,
            correlation_id=self._correlation_id,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MessageBroker",
    "MessageBuilder",
]
