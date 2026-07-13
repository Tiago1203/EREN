"""Boot metrics for the Cognitive Boot Manager.

Collects and calculates boot metrics.

Architecture only -- no implementations.
"""


class BootMetricsCollector:
    """Collects boot metrics."""

    def __init__(self):
        self.boot_attempts = 0
        self.boot_successes = 0
        self.boot_failures = 0
        self.rollbacks = 0
        self.total_duration_ms = 0
        self.steps_completed = 0
        self.steps_failed = 0
        self.steps_skipped = 0

    def record_boot_started(self):
        self.boot_attempts += 1

    def record_boot_success(self, duration_ms: int):
        self.boot_successes += 1
        self.total_duration_ms += duration_ms

    def record_boot_failure(self, duration_ms: int):
        self.boot_failures += 1
        self.total_duration_ms += duration_ms

    def record_step_completed(self):
        self.steps_completed += 1

    def record_step_failed(self):
        self.steps_failed += 1

    def record_step_skipped(self):
        self.steps_skipped += 1

    def record_rollback(self):
        self.rollbacks += 1

    def to_dict(self):
        return {
            "boot_attempts": self.boot_attempts,
            "boot_successes": self.boot_successes,
            "boot_failures": self.boot_failures,
            "rollbacks": self.rollbacks,
            "total_duration_ms": self.total_duration_ms,
            "steps_completed": self.steps_completed,
            "steps_failed": self.steps_failed,
            "steps_skipped": self.steps_skipped,
            "success_rate": (
                self.boot_successes / self.boot_attempts
                if self.boot_attempts > 0
                else 0
            ),
        }
