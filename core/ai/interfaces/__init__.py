"""AI Interfaces - Alias para contracts.

Este módulo existe por compatibilidad y para mantener
una estructura clara. Las interfaces reales están en contracts.
"""

# Re-export from contracts for convenience
from core.ai.contracts import (
    AIProvider,
    AIKernel,
    ModelRegistry,
    AIConfiguration,
    Container,
    Scope,
    Tool,
    ToolRegistry,
    AIContextManager,
    StreamingProvider,
    FunctionCallingProvider,
)

__all__ = [
    "AIProvider",
    "AIKernel",
    "ModelRegistry",
    "AIConfiguration",
    "Container",
    "Scope",
    "Tool",
    "ToolRegistry",
    "AIContextManager",
    "StreamingProvider",
    "FunctionCallingProvider",
]
