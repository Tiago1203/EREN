"""EREN core — Tools engine. Scaffolding only; no functionality yet.

Exposes the Tools engine (registry) and re-exports the external-access tool
contracts from :mod:`core.tools.catalog`.
"""

from .catalog import (
    DICOMTool,
    EmailTool,
    ExternalTool,
    FHIRTool,
    HL7Tool,
    OCRTool,
    PDFTool,
    SupabaseTool,
    ToolCategory,
    VoiceTool,
)
from .engine import ToolsEngine
from .exceptions import (
    ToolAlreadyRegisteredError,
    ToolInvocationError,
    ToolNotFoundError,
    ToolsError,
)
from .interfaces import ToolsPort

__all__ = [
    "ToolsEngine",
    "ToolsError",
    "ToolNotFoundError",
    "ToolAlreadyRegisteredError",
    "ToolInvocationError",
    "ToolsPort",
    "ExternalTool",
    "ToolCategory",
    "SupabaseTool",
    "PDFTool",
    "OCRTool",
    "EmailTool",
    "VoiceTool",
    "FHIRTool",
    "HL7Tool",
    "DICOMTool",
]
