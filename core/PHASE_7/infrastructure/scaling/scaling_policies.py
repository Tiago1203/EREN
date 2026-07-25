"""
PHASE 7 - EPIC 3: Scaling Policies

Predefined scaling policies:
- Conservative (stable)
- Balanced (default)
- Aggressive (fast scaling)
- Cost-optimized (scale down fast)
- Per-service policies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScalingPolicyConfig:
    """Configuración completa de política de scaling."""
    name: str
    description: str

    # Replicas
    min_replicas: int = 1
    max_replicas: int = 10
    default_replicas: int = 2

    # CPU
    cpu_target_percent: float = 70.0
    cpu_scale_up_threshold: float = 75.0
    cpu_scale_down_threshold: float = 40.0

    # Memory
    memory_target_percent: float = 80.0
    memory_scale_up_threshold: float = 85.0
    memory_scale_down_threshold: float = 50.0

    # Requests
    rps_target: float = 1000.0
    rps_per_replica: float = 500.0

    # Timing
    stabilization_window_seconds: int = 300
    scale_up_delay_seconds: int = 60
    scale_down_delay_seconds: int = 300
    cooldown_seconds: int = 300

    # Behavior
    allow_scale_to_zero: bool = False
    block_scale_down_if_no_history: bool = True
    scale_up_rate_limit: int = 5    # Max replicas added per minute


class ScalingPolicies:
    """Políticas predefinidas de scaling."""

    CONSERVATIVE = ScalingPolicyConfig(
        name="conservative",
        description="Stable scaling - prefers keeping more replicas running",
        min_replicas=2,
        max_replicas=5,
        default_replicas=2,
        cpu_target_percent=60.0,
        stabilization_window_seconds=600,
        scale_up_delay_seconds=120,
        scale_down_delay_seconds=600,
        cooldown_seconds=600,
    )

    BALANCED = ScalingPolicyConfig(
        name="balanced",
        description="Balanced scaling - default for most services",
        min_replicas=1,
        max_replicas=10,
        default_replicas=2,
        cpu_target_percent=70.0,
        stabilization_window_seconds=300,
        scale_up_delay_seconds=60,
        scale_down_delay_seconds=300,
        cooldown_seconds=300,
    )

    AGGRESSIVE = ScalingPolicyConfig(
        name="aggressive",
        description="Fast scaling - quick to scale up and down",
        min_replicas=1,
        max_replicas=20,
        default_replicas=2,
        cpu_target_percent=80.0,
        stabilization_window_seconds=60,
        scale_up_delay_seconds=15,
        scale_down_delay_seconds=60,
        cooldown_seconds=60,
    )

    COST_OPTIMIZED = ScalingPolicyConfig(
        name="cost_optimized",
        description="Cost-optimized - scales down aggressively",
        min_replicas=1,
        max_replicas=10,
        default_replicas=1,
        cpu_target_percent=85.0,
        stabilization_window_seconds=60,
        scale_up_delay_seconds=30,
        scale_down_delay_seconds=60,
        cooldown_seconds=120,
        block_scale_down_if_no_history=False,
    )

    @staticmethod
    def for_service(service_type: str) -> ScalingPolicyConfig:
        """Obtiene política apropiada para tipo de servicio."""
        service_policies = {
            "api": ScalingPolicies.BALANCED,
            "web": ScalingPolicies.BALANCED,
            "worker": ScalingPolicies.COST_OPTIMIZED,
            "background": ScalingPolicies.COST_OPTIMIZED,
            "critical": ScalingPolicies.CONSERVATIVE,
            "frontend": ScalingPolicies.BALANCED,
            "database_proxy": ScalingPolicies.CONSERVATIVE,
            "cache": ScalingPolicies.COST_OPTIMIZED,
            "ai_inference": ScalingPolicies.AGGRESSIVE,
            "audit": ScalingPolicies.CONSERVATIVE,
        }
        return service_policies.get(service_type, ScalingPolicies.BALANCED)

    @staticmethod
    def for_load(profile: str) -> ScalingPolicyConfig:
        """Obtiene política para perfil de carga."""
        profiles = {
            "steady": ScalingPolicies.CONSERVATIVE,
            "variable": ScalingPolicies.BALANCED,
            "spiky": ScalingPolicies.AGGRESSIVE,
            "batch": ScalingPolicies.COST_OPTIMIZED,
        }
        return profiles.get(profile, ScalingPolicies.BALANCED)

    @staticmethod
    def custom(
        name: str,
        min_replicas: int = 1,
        max_replicas: int = 10,
        target_utilization: float = 70.0,
        cooldown_seconds: int = 300,
    ) -> ScalingPolicyConfig:
        """Crea política custom."""
        return ScalingPolicyConfig(
            name=name,
            description=f"Custom policy: {name}",
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            cpu_target_percent=target_utilization,
            cooldown_seconds=cooldown_seconds,
        )
