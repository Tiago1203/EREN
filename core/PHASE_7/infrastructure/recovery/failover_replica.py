"""
PHASE 7 - EPIC 3: Failover Replica

Read replica management:
- Primary/replica setup
- Async replication monitoring
- Failover to replica
- Lag monitoring
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ReplicaStatus(str, Enum):
    """Estados de replica."""
    ACTIVE = "active"
    LAGGING = "lagging"
    STOPPED = "stopped"
    CATCHING_UP = "catching_up"
    FAILED = "failed"


@dataclass
class ReadReplica:
    """Read replica."""
    replica_id: str
    host: str
    port: int
    status: ReplicaStatus
    lag_bytes: int = 0
    lag_seconds: float = 0.0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    is_promotable: bool = True
    priority: int = 100


class FailoverReplicaManager:
    """Gestor de failover a replicas de lectura."""

    def __init__(self):
        self._replicas: dict[str, ReadReplica] = {}
        self._primary: Optional[str] = None

    def add_replica(self, replica: ReadReplica) -> None:
        """Añade replica."""
        self._replicas[replica.replica_id] = replica

    def promote_replica(self, replica_id: str) -> bool:
        """Promueve replica a primary."""
        if replica_id not in self._replicas:
            return False

        replica = self._replicas[replica_id]
        if replica.status != ReplicaStatus.ACTIVE:
            return False

        # Check lag is acceptable
        if replica.lag_seconds > 5:
            return False

        self._primary = replica_id
        return True

    def get_replica_status(self) -> dict:
        """Estado de replicas."""
        replicas = []
        for r in self._replicas.values():
            replicas.append({
                "replica_id": r.replica_id,
                "host": r.host,
                "status": r.status.value,
                "lag_seconds": r.lag_seconds,
                "is_promotable": r.is_promotable,
                "priority": r.priority,
            })

        return {
            "primary": self._primary,
            "total_replicas": len(self._replicas),
            "healthy_replicas": sum(1 for r in self._replicas.values() if r.status == ReplicaStatus.ACTIVE),
            "replicas": replicas,
        }
