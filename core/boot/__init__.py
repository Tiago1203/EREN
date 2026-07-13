"""Cognitive Boot Manager (CBM).

The official component for starting EREN in an orderly and reproducible manner.

Architecture only -- no implementations, no business logic.
"""

from core.boot.boot_manager import (
    BootManagerFactory,
    CognitiveBootManager,
)
from core.boot.boot_policy import BootPolicy, BootPolicyPresets
from core.boot.boot_events import BootEventPublisher, BootEventType
from core.boot.boot_metrics import BootMetricsCollector
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
    BootError,
    BootStepError,
    BootTimeoutError,
    BootRollbackError,
    BootConfigurationError,
    BootContractViolationError,
)

__all__ = [
    "CognitiveBootManager",
    "BootManagerFactory",
    "BootPolicy",
    "BootPolicyPresets",
    "BootEventPublisher",
    "BootEventType",
    "BootMetricsCollector",
    "BootTraceCollector",
    "BootTraceEntry",
    "BOOT_SEQUENCE",
    "BootConfiguration",
    "BootResult",
    "BootState",
    "BootStatus",
    "BootStep",
    "BootError",
    "BootStepError",
    "BootTimeoutError",
    "BootRollbackError",
    "BootConfigurationError",
    "BootContractViolationError",
]
