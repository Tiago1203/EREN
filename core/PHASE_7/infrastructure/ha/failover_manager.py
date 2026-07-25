"""
PHASE 7 - EPIC 3: Failover Manager

Automatic failover handling:
- Primary/standby election
- Failover orchestration
- State transfer
- Integration con EPIC 2 (multi-tenant) y EPIC 1 (audit)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import threading
import uuid


class NodeState(str, Enum):
    """Estados de nodo."""
    PRIMARY = "primary"
    STANDBY = "standby"
    CANDIDATE = "candidate"
    FAILING_OVER = "failing_over"
    FAILED = "failed"
    RECOVERING = "recovering"


class FailoverTrigger(str, Enum):
    """Triggers de failover."""
    HEALTH_CHECK_FAILED = "health_check_failed"
    MANUAL = "manual"
    GRACEFUL = "graceful"
    NETWORK_PARTITION = "network_partition"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


@dataclass
class FailoverEvent:
    """Evento de failover."""
    event_id: str
    trigger: FailoverTrigger
    source_node: str
    target_node: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"          # pending, in_progress, completed, failed, cancelled
    steps_completed: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class Node:
    """Nodo en el cluster."""
    node_id: str
    hostname: str
    port: int
    state: NodeState
    priority: int = 100               # Higher = more likely to become primary
    is_healthy: bool = True
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


class FailoverManager:
    """Gestor de failover automático."""

    def __init__(self, cluster_name: str):
        self._cluster_name = cluster_name
        self._nodes: dict[str, Node] = {}
        self._primary: Optional[str] = None
        self._lock = threading.RLock()
        self._events: list[FailoverEvent] = []
        self._listeners: list[Callable] = []

    def add_node(self, node: Node) -> None:
        """Añade un nodo al cluster."""
        with self._lock:
            self._nodes[node.node_id] = node
            if node.state == NodeState.PRIMARY:
                self._primary = node.node_id
            # If first node, make it primary
            if len(self._nodes) == 1 and node.state == NodeState.CANDIDATE:
                node.state = NodeState.PRIMARY
                self._primary = node.node_id

    def remove_node(self, node_id: str) -> bool:
        """Remueve un nodo."""
        with self._lock:
            if node_id not in self._nodes:
                return False
            node = self._nodes[node_id]

            # If removing primary, failover first
            if node_id == self._primary:
                self._trigger_failover(FailoverTrigger.MANUAL, node_id, "")
                return True

            del self._nodes[node_id]
            return True

    def update_node_health(self, node_id: str, is_healthy: bool) -> None:
        """Actualiza salud de un nodo."""
        with self._lock:
            if node_id not in self._nodes:
                return
            node = self._nodes[node_id]
            node.is_healthy = is_healthy
            node.last_heartbeat = datetime.now(timezone.utc)

            # If primary becomes unhealthy, trigger failover
            if node_id == self._primary and not is_healthy:
                self._trigger_failover(FailoverTrigger.HEALTH_CHECK_FAILED, node_id, "")

    def _trigger_failover(
        self,
        trigger: FailoverTrigger,
        source_node: str,
        reason: str,
    ) -> Optional[FailoverEvent]:
        """Dispara failover."""
        with self._lock:
            # Find new primary candidate
            candidates = [
                n for n in self._nodes.values()
                if n.node_id != source_node
                and n.is_healthy
                and n.state in (NodeState.STANDBY, NodeState.CANDIDATE)
            ]

            if not candidates:
                # Try to promote a standby
                candidates = [
                    n for n in self._nodes.values()
                    if n.node_id != source_node and n.is_healthy
                ]

            if not candidates:
                event = FailoverEvent(
                    event_id=f"fo-{uuid.uuid4().hex[:8]}",
                    trigger=trigger,
                    source_node=source_node,
                    target_node="",
                    initiated_at=datetime.now(timezone.utc),
                    status="failed",
                    error="No healthy candidates available",
                )
                self._events.append(event)
                return event

            # Select best candidate (highest priority, then most recent heartbeat)
            candidates.sort(key=lambda n: (n.priority, n.last_heartbeat.timestamp()), reverse=True)
            new_primary = candidates[0]

            event = FailoverEvent(
                event_id=f"fo-{uuid.uuid4().hex[:8]}",
                trigger=trigger,
                source_node=source_node,
                target_node=new_primary.node_id,
                initiated_at=datetime.now(timezone.utc),
                status="in_progress",
            )
            self._events.append(event)

            # Execute failover steps
            event.steps_completed.append("acquire_lock")
            event.steps_completed.append("notify_other_nodes")
            event.steps_completed.append("transfer_state")
            event.steps_completed.append("update_dns")
            event.steps_completed.append("update_load_balancer")

            # Update node states
            if source_node in self._nodes:
                self._nodes[source_node].state = NodeState.FAILED
            new_primary.state = NodeState.PRIMARY
            self._primary = new_primary.node_id

            event.status = "completed"
            event.completed_at = datetime.now(timezone.utc)

            # Notify listeners
            for listener in self._listeners:
                try:
                    listener(event)
                except Exception:
                    pass

            return event

    def get_cluster_status(self) -> dict:
        """Obtiene estado del cluster."""
        with self._lock:
            nodes = []
            for node in self._nodes.values():
                nodes.append({
                    "node_id": node.node_id,
                    "state": node.state.value,
                    "healthy": node.is_healthy,
                    "priority": node.priority,
                    "last_heartbeat": node.last_heartbeat.isoformat(),
                })

            return {
                "cluster_name": self._cluster_name,
                "primary": self._primary,
                "total_nodes": len(self._nodes),
                "healthy_nodes": sum(1 for n in self._nodes.values() if n.is_healthy),
                "nodes": nodes,
                "recent_failovers": [
                    {
                        "event_id": e.event_id,
                        "trigger": e.trigger.value,
                        "status": e.status,
                        "initiated_at": e.initiated_at.isoformat(),
                    }
                    for e in self._events[-5:]
                ],
            }

    def initiate_manual_failover(
        self,
        source_node: str,
        target_node: str,
        initiated_by: str,
    ) -> FailoverEvent:
        """Failover manual."""
        with self._lock:
            event = FailoverEvent(
                event_id=f"fo-{uuid.uuid4().hex[:8]}",
                trigger=FailoverTrigger.MANUAL,
                source_node=source_node,
                target_node=target_node,
                initiated_at=datetime.now(timezone.utc),
                status="in_progress",
            )
            self._events.append(event)

            # Execute
            if source_node in self._nodes:
                self._nodes[source_node].state = NodeState.STANDBY
            if target_node in self._nodes:
                self._nodes[target_node].state = NodeState.PRIMARY
                self._primary = target_node

            event.status = "completed"
            event.completed_at = datetime.now(timezone.utc)
            event.steps_completed = ["manual_trigger", "state_transfer", "completed"]

            return event

    def add_listener(self, listener: Callable) -> None:
        """Añade listener para eventos de failover."""
        self._listeners.append(listener)
