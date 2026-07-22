"""Cognitive Boot Manager (CBM).

The official component for starting EREN in an orderly and reproducible manner.

Architecture only -- no implementations, no business logic.
"""

from core.PHASE_1.infrastructure.boot.boot_events import BootEventPublisher, BootEventType
from core.PHASE_1.infrastructure.boot.boot_manager import (
    BootManagerFactory,
    CognitiveBootManager,
)
from core.PHASE_1.infrastructure.boot.boot_metrics import BootMetricsCollector
from core.PHASE_1.infrastructure.boot.boot_policy import BootPolicy, BootPolicyPresets
from core.PHASE_1.infrastructure.boot.boot_trace import BootTraceCollector, BootTraceEntry
from core.PHASE_1.infrastructure.boot.boot_types import (
    BOOT_SEQUENCE,
    BootConfiguration,
    BootResult,
    BootState,
    BootStatus,
    BootStep,
)
from core.PHASE_1.infrastructure.boot.exceptions import (
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
