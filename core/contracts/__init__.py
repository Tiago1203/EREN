"""EREN contracts layer — the common interfaces every engine implements.

Pure, documented interfaces (``typing.Protocol``). No logic, AI, or agents.
Import contracts from here rather than from the individual modules.
"""

from .base import CognitiveEngine, SupportsLifecycle
from .diagnostic import Diagnostic
from .knowledge import Knowledge
from .memory import Memory
from .planner import Planner
from .reasoning import Reasoning
from .tool import Tool
from .workflow import Workflow
from .agent import AgentContract, AgentStatus, TaskStatus, AgentTask, AgentResult
from .provider import (
    ProviderContract,
    ProviderType,
    ProviderHealth,
    GenerationRequest,
    GenerationResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)

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
