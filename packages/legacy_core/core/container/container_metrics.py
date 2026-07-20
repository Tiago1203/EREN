"""Container Metrics for the Cognitive Dependency Injection Container.

Collects and calculates container metrics.

Architecture only -- no implementations.
"""


class ContainerMetricsCollector:
    """Collects container metrics."""

    def __init__(self):
        self.services_registered = 0
        self.services_resolved = 0
        self.resolution_errors = 0
        self.circular_dependencies_detected = 0
        self.scopes_created = 0
        self.scopes_disposed = 0
        self.active_scopes = 0
        self.factories_executed = 0
        self.singletons_created = 0
        self.total_resolution_time_ms = 0
        self.total_validation_time_ms = 0

    def record_service_registered(self):
        self.services_registered += 1

    def record_service_resolved(self, time_ms: int = 0):
        self.services_resolved += 1
        self.total_resolution_time_ms += time_ms

    def record_resolution_error(self):
        self.resolution_errors += 1

    def record_circular_dependency(self):
        self.circular_dependencies_detected += 1

    def record_scope_created(self):
        self.scopes_created += 1
        self.active_scopes += 1

    def record_scope_disposed(self):
        self.scopes_disposed += 1
        self.active_scopes = max(0, self.active_scopes - 1)

    def record_factory_executed(self):
        self.factories_executed += 1

    def record_singleton_created(self):
        self.singletons_created += 1

    def record_validation_time(self, time_ms: int):
        self.total_validation_time_ms += time_ms

    def get_average_resolution_time(self) -> float:
        if self.services_resolved == 0:
            return 0
        return self.total_resolution_time_ms / self.services_resolved

    def to_dict(self):
        return {
            "services_registered": self.services_registered,
            "services_resolved": self.services_resolved,
            "resolution_errors": self.resolution_errors,
            "circular_dependencies_detected": self.circular_dependencies_detected,
            "scopes_created": self.scopes_created,
            "scopes_disposed": self.scopes_disposed,
            "active_scopes": self.active_scopes,
            "factories_executed": self.factories_executed,
            "singletons_created": self.singletons_created,
            "total_resolution_time_ms": self.total_resolution_time_ms,
            "average_resolution_time_ms": self.get_average_resolution_time(),
            "total_validation_time_ms": self.total_validation_time_ms,
        }
