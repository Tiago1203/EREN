"""Lifecycle metrics for the Cognitive Lifecycle Manager."""


class LifecycleMetricsCollector:
    """Collects lifecycle metrics."""

    def __init__(self):
        self.transitions = 0
        self.invalid_transitions = 0
        self.completed = 0
        self.failed = 0
        self.cancelled = 0
        self.archived = 0

    def record_transition(self):
        self.transitions += 1

    def record_invalid_transition(self):
        self.invalid_transitions += 1

    def record_completed(self):
        self.completed += 1

    def record_failed(self):
        self.failed += 1

    def record_cancelled(self):
        self.cancelled += 1

    def record_archived(self):
        self.archived += 1

    def to_dict(self):
        return {
            "transitions": self.transitions,
            "invalid_transitions": self.invalid_transitions,
            "completed": self.completed,
            "failed": self.failed,
            "cancelled": self.cancelled,
            "archived": self.archived,
        }
