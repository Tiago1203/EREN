"""Cognitive Boot Manager (CBM).

The official component for starting EREN in an orderly and reproducible manner.

Architecture only -- no implementations, no business logic.
"""

from core.boot.boot_events import BootEventPublisher, BootEventType
from core.boot.boot_manager import (
    BootManagerFactory,
    CognitiveBootManager,
)
from core.boot.boot_metrics import BootMetricsCollector
from core.boot.boot_policy import BootPolicy, BootPolicyPresets
from core.boot.boot_trace import BootTraceCollector, BootTraceEntry
from core.boot.boot_types import (
    BOOT_SEQUENCE,
    BootConfiguration,
    BootResult,
    BootState,
    BootStatus,
    BootStep,
)
from core.boot.exceptions import (
    BootConfigurationError,
    BootContractViolationError,
    BootError,
    BootRollbackError,
    BootStepError,
    BootTimeoutError,
)

__all__ = [
    "BOOT_SEQUENCE",
    "BootConfiguration",
    "BootConfigurationError",
    "BootContractViolationError",
    "BootError",
    "BootEventPublisher",
    "BootEventType",
    "BootManagerFactory",
    "BootMetricsCollector",
    "BootPolicy",
    "BootPolicyPresets",
    "BootResult",
    "BootRollbackError",
    "BootState",
    "BootStatus",
    "BootStep",
    "BootStepError",
    "BootTimeoutError",
    "BootTraceCollector",
    "BootTraceEntry",
    "CognitiveBootManager",
]
