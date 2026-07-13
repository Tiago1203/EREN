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

__all__ = [
    "CognitiveEngine",
    "Diagnostic",
    "Knowledge",
    "Memory",
    "Planner",
    "Reasoning",
    "SupportsLifecycle",
    "Tool",
    "Workflow",
]
