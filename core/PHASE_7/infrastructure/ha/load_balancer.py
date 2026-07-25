"""
PHASE 7 - EPIC 3: Load Balancer

Request distribution and load balancing:
- Round robin, weighted, least connections
- Health-aware routing
- Connection pooling
- Integration con EPIC 2 (multi-tenant)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import random
import threading


class Algorithm(str, Enum):
    """Algoritmos de balanceo."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"
    RANDOM = "random"


@dataclass
class Backend:
    """Backend server."""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    healthy: bool = True
    last_health_check: Optional[datetime] = None
    failure_count: int = 0
    metadata: dict = field(default_factory=dict)

    def is_available(self) -> bool:
        return self.healthy and self.current_connections < self.max_connections


@dataclass
class LoadBalancerConfig:
    """Configuración del load balancer."""
    algorithm: Algorithm = Algorithm.ROUND_ROBIN
    health_check_interval: int = 30       # seconds
    health_check_timeout: int = 5           # seconds
    max_failures: int = 3
    recovery_threshold: int = 3
    connection_timeout: int = 30
    idle_timeout: int = 120
    enable_access_log: bool = True
    sticky_sessions: bool = False
    sticky_cookie_name: str = "EREN_SESSION"


class LoadBalancer:
    """Load balancer principal."""

    def __init__(self, config: Optional[LoadBalancerConfig] = None):
        self._config = config or LoadBalancerConfig()
        self._backends: dict[str, Backend] = {}
        self._round_robin_index: dict[str, int] = {}
        self._lock = threading.Lock()
        self._connection_count: dict[str, int] = {}

    def add_backend(self, backend: Backend) -> None:
        """Añade un backend."""
        with self._lock:
            self._backends[backend.id] = backend
            self._round_robin_index[backend.id] = 0
            self._connection_count[backend.id] = 0

    def remove_backend(self, backend_id: str) -> bool:
        """Remueve un backend."""
        with self._lock:
            if backend_id in self._backends:
                del self._backends[backend_id]
                return True
            return False

    def get_backend(self, client_ip: str = "", request_id: str = "") -> Optional[Backend]:
        """Selecciona el mejor backend según el algoritmo."""
        available = [b for b in self._backends.values() if b.is_available()]
        if not available:
            return None

        with self._lock:
            if self._config.algorithm == Algorithm.ROUND_ROBIN:
                return self._round_robin(available)
            elif self._config.algorithm == Algorithm.LEAST_CONNECTIONS:
                return self._least_connections(available)
            elif self._config.algorithm == Algorithm.WEIGHTED:
                return self._weighted(available)
            elif self._config.algorithm == Algorithm.IP_HASH:
                return self._ip_hash(available, client_ip)
            else:
                return self._random(available)

    def _round_robin(self, backends: list[Backend]) -> Backend:
        """Round robin simple."""
        # Rotate through backends
        for _ in range(len(backends)):
            idx = self._round_robin_index.get(backends[0].id, 0)
            selected = backends[idx % len(backends)]
            self._round_robin_index[selected.id] = (idx + 1) % len(backends)
            return selected
        return backends[0]

    def _least_connections(self, backends: list[Backend]) -> Backend:
        """Menos conexiones activas."""
        return min(backends, key=lambda b: b.current_connections)

    def _weighted(self, backends: list[Backend]) -> Backend:
        """Weighted round robin."""
        total_weight = sum(b.weight for b in backends)
        if total_weight == 0:
            return backends[0]
        r = random.randint(1, total_weight)
        cumulative = 0
        for backend in backends:
            cumulative += backend.weight
            if cumulative >= r:
                return backend
        return backends[0]

    def _ip_hash(self, backends: list[Backend], client_ip: str) -> Backend:
        """IP hash for sticky sessions."""
        if not client_ip:
            return backends[0]
        hash_val = sum(ord(c) * (i + 1) for i, c in enumerate(client_ip))
        return backends[hash_val % len(backends)]

    def _random(self, backends: list[Backend]) -> Backend:
        """Random selection."""
        return random.choice(backends)

    def record_connection(self, backend_id: str) -> None:
        """Registra una conexión."""
        with self._lock:
            if backend_id in self._backends:
                self._backends[backend_id].current_connections += 1

    def release_connection(self, backend_id: str) -> None:
        """Libera una conexión."""
        with self._lock:
            if backend_id in self._backends:
                b = self._backends[backend_id]
                b.current_connections = max(0, b.current_connections - 1)

    def mark_backend_unhealthy(self, backend_id: str) -> None:
        """Marca un backend como no saludable."""
        with self._lock:
            if backend_id in self._backends:
                b = self._backends[backend_id]
                b.failure_count += 1
                if b.failure_count >= self._config.max_failures:
                    b.healthy = False

    def mark_backend_healthy(self, backend_id: str) -> None:
        """Marca un backend como saludable."""
        with self._lock:
            if backend_id in self._backends:
                b = self._backends[backend_id]
                b.failure_count = 0
                b.healthy = True
                b.last_health_check = datetime.now(timezone.utc)

    def get_status(self) -> dict:
        """Obtiene estado del load balancer."""
        return {
            "total_backends": len(self._backends),
            "healthy_backends": sum(1 for b in self._backends.values() if b.healthy),
            "total_connections": sum(b.current_connections for b in self._backends.values()),
            "algorithm": self._config.algorithm.value,
            "backends": [
                {
                    "id": b.id,
                    "healthy": b.healthy,
                    "connections": b.current_connections,
                    "last_check": b.last_health_check.isoformat() if b.last_health_check else None,
                }
                for b in self._backends.values()
            ],
        }
