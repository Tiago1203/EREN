"""EREN contracts layer — the common interfaces every engine implements.

Pure, documented interfaces (``typing.Protocol``). No logic, AI, or agents.
Import contracts from here rather than from the individual modules.
"""

from .agent import AgentContract, AgentResult, AgentStatus, AgentTask, TaskStatus
from .base import CognitiveEngine, SupportsLifecycle
from .diagnostic import Diagnostic
from .knowledge import Knowledge
from .memory import Memory
from .planner import Planner
from .provider import (
    EmbeddingRequest,
    EmbeddingResponse,
    GenerationRequest,
    GenerationResponse,
    ProviderContract,
    ProviderHealth,
    ProviderType,
)
from .reasoning import Reasoning
from .tool import Tool
from .workflow import Workflow

__all__ = [
    # Base contracts
    "CognitiveEngine",
    "SupportsLifecycle",
    # Domain contracts
    "Diagnostic",
    "Knowledge",
    "Memory",
    "Planner",
    "Reasoning",
    "Tool",
    "Workflow",
    # New contracts
    "AgentContract",
    "AgentStatus",
    "TaskStatus",
    "AgentTask",
    "AgentResult",
    "ProviderContract",
    "ProviderType",
    "ProviderHealth",
    "GenerationRequest",
    "GenerationResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
]
