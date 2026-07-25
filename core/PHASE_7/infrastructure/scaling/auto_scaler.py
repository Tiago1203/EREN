"""
PHASE 7 - EPIC 3: Auto Scaler

Horizontal Pod Autoscaler implementation:
- Metric-based scaling
- Scaling policies
- Cooldown management
- Integration con EPIC 2 (multi-tenant quotas)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
import threading


class ScalingAction(str, Enum):
    """Acciones de scaling."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_STABLE = "stable"
    NO_ACTION = "no_action"


@dataclass
class ScalingDecision:
    """Decisión de scaling."""
    action: ScalingAction
    current_replicas: int
    desired_replicas: int
    reason: str
    metrics: dict
    timestamp: datetime


@dataclass
class ScalingMetric:
    """Métrica para scaling."""
    name: str
    current_value: float
    target_value: float
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None


@dataclass
class ScalingPolicy:
    """Política de scaling."""
    name: str
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_percent: float = 70.0
    target_memory_percent: float = 80.0
    target_requests_per_second: float = 1000.0
    stabilization_window_seconds: int = 300   # 5 min
    scale_up_stabilization_seconds: int = 60   # 1 min
    scale_down_stabilization_seconds: int = 300  # 5 min
    cooldown_seconds: int = 300


class AutoScaler:
    """Auto scaler principal."""

    def __init__(
        self,
        service_name: str,
        policy: Optional[ScalingPolicy] = None,
    ):
        self._service_name = service_name
        self._policy = policy or ScalingPolicy(name=service_name)
        self._current_replicas = 1
        self._desired_replicas = 1
        self._last_scale_time: Optional[datetime] = None
        self._scale_history: list[ScalingDecision] = []
        self._lock = threading.Lock()
        self._pending_scale: Optional[int] = None
        self._pending_scale_time: Optional[datetime] = None

    def update_metrics(
        self,
        cpu_percent: float,
        memory_percent: float,
        requests_per_second: float,
        active_connections: int,
    ) -> ScalingDecision:
        """Actualiza métricas y toma decisión de scaling."""
        with self._lock:
            decision = self._evaluate(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                rps=requests_per_second,
                connections=active_connections,
            )

            # Only update desired if not in cooldown
            if self._can_scale(decision.action):
                self._desired_replicas = decision.desired_replicas
                if decision.action in (ScalingAction.SCALE_UP, ScalingAction.SCALE_DOWN):
                    self._last_scale_time = datetime.now(timezone.utc)

            self._scale_history.append(decision)
            if len(self._scale_history) > 100:
                self._scale_history = self._scale_history[-100:]

            return decision

    def _can_scale(self, action: ScalingAction) -> bool:
        """Check si puede escalar."""
        if action == ScalingAction.NO_ACTION or action == ScalingAction.SCALE_STABLE:
            return True

        if self._last_scale_time:
            elapsed = (datetime.now(timezone.utc) - self._last_scale_time).total_seconds()
            if elapsed < self._policy.cooldown_seconds:
                return False

        # Check pending scale
        if self._pending_scale is not None:
            elapsed = (datetime.now(timezone.utc) - self._pending_scale_time).total_seconds()
            if elapsed > 60:
                self._pending_scale = None
                self._pending_scale_time = None

        return True

    def _evaluate(
        self,
        cpu_percent: float,
        memory_percent: float,
        rps: float,
        connections: int,
    ) -> ScalingDecision:
        """Evalúa métricas y decide scaling."""
        p = self._policy
        metrics = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "requests_per_second": rps,
            "active_connections": connections,
        }

        # Calculate utilization
        cpu_util = cpu_percent / 100
        memory_util = memory_percent / 100
        rps_util = rps / p.target_requests_per_second if p.target_requests_per_second > 0 else 0

        max_util = max(cpu_util, memory_util, rps_util)

        # Scale up criteria
        scale_up = max_util > (p.target_cpu_percent / 100)
        scale_down = max_util < ((p.target_cpu_percent / 100) * 0.5)  # 50% of target

        if scale_up:
            # Calculate desired replicas based on utilization
            if max_util > 0:
                desired = max(1, min(
                    p.max_replicas,
                    int(self._current_replicas * max_util / (p.target_cpu_percent / 100)) + 1
                ))
            else:
                desired = self._current_replicas + 1

            desired = max(p.min_replicas, min(p.max_replicas, desired))
            action = ScalingAction.SCALE_UP
            reason = f"High utilization: {max_util*100:.1f}% (target: {p.target_cpu_percent}%)"

        elif scale_down:
            desired = max(p.min_replicas, int(self._current_replicas * max_util / (p.target_cpu_percent / 100)))

            if desired < self._current_replicas:
                action = ScalingAction.SCALE_DOWN
                reason = f"Low utilization: {max_util*100:.1f}% (target: {p.target_cpu_percent/2}%)"
            else:
                action = ScalingAction.SCALE_STABLE
                reason = "Utilization within acceptable range"

        else:
            desired = self._current_replicas
            action = ScalingAction.STABLE
            reason = "Metrics within target range"

        return ScalingDecision(
            action=action,
            current_replicas=self._current_replicas,
            desired_replicas=desired,
            reason=reason,
            metrics=metrics,
            timestamp=datetime.now(timezone.utc),
        )

    def execute_scale(self, replicas: int) -> bool:
        """Ejecuta el scaling (llamado por el orchestrator)."""
        with self._lock:
            replicas = max(self._policy.min_replicas, min(self._policy.max_replicas, replicas))

            if replicas != self._current_replicas:
                self._current_replicas = replicas
                self._last_scale_time = datetime.now(timezone.utc)
                return True
            return False

    def get_status(self) -> dict:
        """Obtiene estado del autoscaler."""
        with self._lock:
            return {
                "service_name": self._service_name,
                "current_replicas": self._current_replicas,
                "desired_replicas": self._desired_replicas,
                "min_replicas": self._policy.min_replicas,
                "max_replicas": self._policy.max_replicas,
                "last_scale_time": self._last_scale_time.isoformat() if self._last_scale_time else None,
                "in_cooldown": self._last_scale_time is not None and (
                    (datetime.now(timezone.utc) - self._last_scale_time).total_seconds()
                    < self._policy.cooldown_seconds
                ),
                "recent_decisions": [
                    {
                        "action": d.action.value,
                        "replicas": d.desired_replicas,
                        "reason": d.reason,
                        "at": d.timestamp.isoformat(),
                    }
                    for d in self._scale_history[-5:]
                ],
            }

    def get_scaling_recommendations(self) -> dict:
        """Obtiene recomendaciones de scaling."""
        with self._lock:
            last = self._scale_history[-1] if self._scale_history else None

            recommendations = []
            if last:
                if last.action == ScalingAction.SCALE_UP:
                    recommendations.append({
                        "type": "scale_up",
                        "suggested_replicas": last.desired_replicas,
                        "reason": last.reason,
                    })
                elif last.action == ScalingAction.SCALE_DOWN:
                    recommendations.append({
                        "type": "scale_down",
                        "suggested_replicas": last.desired_replicas,
                        "reason": last.reason,
                    })

            return {
                "service_name": self._service_name,
                "current_replicas": self._current_replicas,
                "recommendations": recommendations,
            }
