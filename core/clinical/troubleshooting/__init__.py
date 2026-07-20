"""Troubleshooting Engine."""
from dataclasses import dataclass
from enum import Enum


class TroubleshootingStep:
    step_number: int
    action: str
    verification: str
    safety_check: str


class TroubleshootingResult:
    steps: list[TroubleshootingStep]
    estimated_time: str
    required_tools: list[str]
    safety_warnings: list[str]


# Import engine for convenience
from core.clinical.troubleshooting.engine import (
    TroubleshootingEngine,
    get_troubleshooting_engine,
    TroubleshootingStep,
    TroubleshootingResult,
)

__all__ = [
    "TroubleshootingStep",
    "TroubleshootingResult",
    "TroubleshootingEngine",
    "get_troubleshooting_engine",
]
