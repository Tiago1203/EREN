"""Composition Metrics for the Cognitive Composition Root.

Collects and calculates composition metrics.

Architecture only -- no implementations.
"""


class CompositionMetricsCollector:
    """Collects composition metrics."""

    def __init__(self):
        self.modules_registered = 0
        self.modules_loaded = 0
        self.modules_initialized = 0
        self.modules_failed = 0
        self.contracts_registered = 0
        self.services_registered = 0
        self.total_build_time_ms = 0
        self.total_validation_time_ms = 0
        self.build_errors = 0

    def record_module_registered(self):
        self.modules_registered += 1

    def record_module_loaded(self):
        self.modules_loaded += 1

    def record_module_initialized(self):
        self.modules_initialized += 1

    def record_module_failed(self):
        self.modules_failed += 1

    def record_contract_registered(self):
        self.contracts_registered += 1

    def record_service_registered(self):
        self.services_registered += 1

    def record_build_time(self, time_ms: int):
        self.total_build_time_ms += time_ms

    def record_validation_time(self, time_ms: int):
        self.total_validation_time_ms += time_ms

    def record_build_error(self):
        self.build_errors += 1

    def get_average_build_time(self) -> float:
        if self.modules_loaded == 0:
            return 0
        return self.total_build_time_ms / self.modules_loaded

    def to_dict(self):
        return {
            "modules_registered": self.modules_registered,
            "modules_loaded": self.modules_loaded,
            "modules_initialized": self.modules_initialized,
            "modules_failed": self.modules_failed,
            "contracts_registered": self.contracts_registered,
            "services_registered": self.services_registered,
            "total_build_time_ms": self.total_build_time_ms,
            "average_build_time_ms": self.get_average_build_time(),
            "total_validation_time_ms": self.total_validation_time_ms,
            "build_errors": self.build_errors,
        }
