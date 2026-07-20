"""Troubleshooting Engine."""
from dataclasses import dataclass


@dataclass
class TroubleshootingStep:
    step_number: int
    action: str
    verification: str
    safety_check: str


@dataclass
class TroubleshootingResult:
    steps: list[TroubleshootingStep]
    estimated_time: str
    required_tools: list[str]
    safety_warnings: list[str]
