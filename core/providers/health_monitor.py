"""Health Monitor for EREN OS Multi-Provider Layer.

Monitors provider health and availability.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.providers.provider import BaseProvider


class HealthStatus(str, Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    provider_id: str
    status: HealthStatus
    latency_ms: int
    timestamp: datetime
    message: str = ""
    is_circuit_open: bool = False
    consecutive_failures: int = 0
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_id": self.provider_id,
            "status": self.status.value,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "is_circuit_open": self.is_circuit_open,
            "consecutive_failures": self.consecutive_failures,
            "details": self.details,
        }


@dataclass
class HealthMetrics:
    """Health metrics for a provider."""

    provider_id: str
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    average_latency_ms: float = 0.0
    min_latency_ms: int = 0
    max_latency_ms: int = 0
    last_check: datetime | None = None
    last_success: datetime | None = None
    last_failure: datetime | None = None
    uptime_seconds: float = 0.0
    consecutive_failures: int = 0
    consecutive_successes: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_checks == 0:
            return 100.0
        return (self.successful_checks / self.total_checks) * 100

    @property
    def is_healthy(self) -> bool:
        """Check if provider is healthy based on metrics."""
        return self.success_rate >= 80.0 and self.consecutive_failures < 3

    def record_check(self, success: bool, latency_ms: int) -> None:
        """Record a health check result."""
        self.total_checks += 1
        self.last_check = datetime.now(UTC)

        if success:
            self.successful_checks += 1
            self.last_success = datetime.now(UTC)
            self.consecutive_successes += 1
            self.consecutive_failures = 0
        else:
            self.failed_checks += 1
            self.last_failure = datetime.now(UTC)
            self.consecutive_failures += 1
            self.consecutive_successes = 0

        # Update latency metrics
        if self.total_checks == 1:
            self.average_latency_ms = float(latency_ms)
            self.min_latency_ms = latency_ms
            self.max_latency_ms = latency_ms
        else:
            self.average_latency_ms = (
                (self.average_latency_ms * (self.total_checks - 1) + latency_ms)
                / self.total_checks
            )
            self.min_latency_ms = min(self.min_latency_ms, latency_ms)
            self.max_latency_ms = max(self.max_latency_ms, latency_ms)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_id": self.provider_id,
            "total_checks": self.total_checks,
            "successful_checks": self.successful_checks,
            "failed_checks": self.failed_checks,
            "success_rate": self.success_rate,
            "average_latency_ms": self.average_latency_ms,
            "min_latency_ms": self.min_latency_ms,
            "max_latency_ms": self.max_latency_ms,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "uptime_seconds": self.uptime_seconds,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "is_healthy": self.is_healthy,
        }


class HealthMonitor:
    """Monitors provider health and availability.

    Features:
    - Periodic health checks
    - Latency tracking
    - Consecutive failure detection
    - Health status callbacks
    - Metrics collection
    """

    def __init__(
        self,
        check_interval_seconds: int = 60,
        timeout_seconds: int = 10,
        max_consecutive_failures: int = 3,
    ):
        """Initialize health monitor.

        Args:
            check_interval_seconds: Interval between health checks.
            timeout_seconds: Timeout for health check requests.
            max_consecutive_failures: Max consecutive failures before marking unhealthy.
        """
        self._check_interval = check_interval_seconds
        self._timeout = timeout_seconds
        self._max_consecutive_failures = max_consecutive_failures

        self._providers: dict[str, BaseProvider] = {}
        self._health_metrics: dict[str, HealthMetrics] = {}
        self._health_status: dict[str, HealthStatus] = {}
        self._last_results: dict[str, HealthCheckResult] = {}

        self._lock = threading.RLock()
        self._running = False
        self._check_task: asyncio.Task | None = None

        self._callbacks: list[Callable[[str, HealthCheckResult], None]] = []

    @property
    def check_interval(self) -> int:
        """Get check interval in seconds."""
        return self._check_interval

    @check_interval.setter
    def check_interval(self, value: int) -> None:
        """Set check interval in seconds."""
        self._check_interval = max(1, value)

    def register_provider(self, provider: BaseProvider) -> None:
        """Register a provider for health monitoring.

        Args:
            provider: Provider to monitor.
        """
        with self._lock:
            provider_id = provider.provider_id
            self._providers[provider_id] = provider
            self._health_metrics[provider_id] = HealthMetrics(provider_id=provider_id)
            self._health_status[provider_id] = HealthStatus.UNKNOWN

    def unregister_provider(self, provider_id: str) -> None:
        """Unregister a provider from health monitoring.

        Args:
            provider_id: Provider identifier.
        """
        with self._lock:
            self._providers.pop(provider_id, None)
            self._health_metrics.pop(provider_id, None)
            self._health_status.pop(provider_id, None)
            self._last_results.pop(provider_id, None)

    def on_health_change(self, callback: Callable[[str, HealthCheckResult], None]) -> None:
        """Register a health change callback.

        Args:
            callback: Callback function(provider_id, result).
        """
        with self._lock:
            if callback not in self._callbacks:
                self._callbacks.append(callback)

    def get_health_status(self, provider_id: str) -> HealthStatus:
        """Get current health status of a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Current health status.
        """
        with self._lock:
            return self._health_status.get(provider_id, HealthStatus.UNKNOWN)

    def get_health_metrics(self, provider_id: str) -> HealthMetrics | None:
        """Get health metrics for a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Health metrics or None.
        """
        with self._lock:
            return self._health_metrics.get(provider_id)

    def get_last_result(self, provider_id: str) -> HealthCheckResult | None:
        """Get last health check result for a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Last health check result or None.
        """
        with self._lock:
            return self._last_results.get(provider_id)

    def get_all_health_status(self) -> dict[str, HealthStatus]:
        """Get health status for all providers.

        Returns:
            Dictionary of provider_id -> health status.
        """
        with self._lock:
            return dict(self._health_status)

    def get_all_metrics(self) -> dict[str, HealthMetrics]:
        """Get health metrics for all providers.

        Returns:
            Dictionary of provider_id -> health metrics.
        """
        with self._lock:
            return dict(self._health_metrics)

    async def check_provider(self, provider_id: str) -> HealthCheckResult:
        """Perform a health check on a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Health check result.
        """
        from core.providers.exceptions import ProviderException

        with self._lock:
            if provider_id not in self._providers:
                return HealthCheckResult(
                    provider_id=provider_id,
                    status=HealthStatus.UNKNOWN,
                    latency_ms=0,
                    timestamp=datetime.now(UTC),
                    message="Provider not registered",
                )
            provider = self._providers[provider_id]

        start_time = time.time()
        try:
            health = await asyncio.wait_for(
                asyncio.to_thread(provider.health_check),
                timeout=self._timeout,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Determine status
            if health.healthy and latency_ms < 1000:
                status = HealthStatus.HEALTHY
                message = "Provider is healthy"
            elif health.healthy:
                status = HealthStatus.DEGRADED
                message = f"Provider is healthy but slow ({latency_ms}ms)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Provider is unhealthy: {health.message}"

            result = HealthCheckResult(
                provider_id=provider_id,
                status=status,
                latency_ms=latency_ms,
                timestamp=datetime.now(UTC),
                message=message,
                details=health.to_dict() if hasattr(health, "to_dict") else {},
            )

        except asyncio.TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            result = HealthCheckResult(
                provider_id=provider_id,
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                timestamp=datetime.now(UTC),
                message="Health check timed out",
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            result = HealthCheckResult(
                provider_id=provider_id,
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                timestamp=datetime.now(UTC),
                message=f"Health check failed: {str(e)}",
            )

        # Update metrics and status
        with self._lock:
            self._last_results[provider_id] = result

            if provider_id in self._health_metrics:
                metrics = self._health_metrics[provider_id]
                success = result.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)
                metrics.record_check(success, result.latency_ms)

            self._health_status[provider_id] = result.status

        # Notify callbacks
        self._notify_callbacks(provider_id, result)

        return result

    async def check_all_providers(self) -> dict[str, HealthCheckResult]:
        """Perform health checks on all registered providers.

        Returns:
            Dictionary of provider_id -> health check result.
        """
        results = {}
        provider_ids = list(self._providers.keys())

        for provider_id in provider_ids:
            results[provider_id] = await self.check_provider(provider_id)

        return results

    def start_monitoring(self) -> None:
        """Start periodic health monitoring."""
        if self._running:
            return

        self._running = True
        self._check_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self) -> None:
        """Stop periodic health monitoring."""
        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
            self._check_task = None

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self.check_all_providers()
            except Exception:
                pass

            await asyncio.sleep(self._check_interval)

    def _notify_callbacks(self, provider_id: str, result: HealthCheckResult) -> None:
        """Notify health change callbacks.

        Args:
            provider_id: Provider identifier.
            result: Health check result.
        """
        for callback in self._callbacks:
            try:
                callback(provider_id, result)
            except Exception:
                pass

    def reset_metrics(self, provider_id: str | None = None) -> None:
        """Reset health metrics.

        Args:
            provider_id: Provider to reset, or None for all.
        """
        with self._lock:
            if provider_id:
                if provider_id in self._health_metrics:
                    self._health_metrics[provider_id] = HealthMetrics(provider_id=provider_id)
            else:
                for pid in self._health_metrics:
                    self._health_metrics[pid] = HealthMetrics(provider_id=pid)

    def __len__(self) -> int:
        """Get number of monitored providers."""
        with self._lock:
            return len(self._providers)

    def __contains__(self, provider_id: str) -> bool:
        """Check if provider is monitored."""
        with self._lock:
            return provider_id in self._providers
