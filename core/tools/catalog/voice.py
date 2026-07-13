"""Contract for the Voice tool — governed speech access.

Speech-to-text (transcription) and text-to-speech (synthesis) through a single
controlled capability. Contract only — no logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .base import ExternalTool


@dataclass(frozen=True, slots=True)
class AudioClip:
    """An audio buffer, referenced by location or raw bytes."""

    uri: str = ""
    content: bytes | None = None
    mime_type: str = "audio/wav"


@dataclass(frozen=True, slots=True)
class Transcript:
    """Text recognized from audio."""

    text: str = ""
    language: str = ""
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class SpeechRequest:
    """A request to synthesize speech from text."""

    text: str = ""
    voice: str = ""
    language: str = ""


@runtime_checkable
class VoiceTool(ExternalTool, Protocol):
    """Governed speech-to-text and text-to-speech."""

    def transcribe(self, clip: AudioClip) -> Transcript:
        """Transcribe *clip* to text."""
        ...

    def synthesize(self, request: SpeechRequest) -> AudioClip:
        """Synthesize speech audio for *request*."""
        ...
