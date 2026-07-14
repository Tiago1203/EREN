"""EREN tools catalog — contracts for external-access capabilities.

Every external access in EREN is modeled as a *tool* contract here. These are
pure ``typing.Protocol`` interfaces (plus their typed I/O models) — no logic, AI,
or agents. Concrete vendor adapters live elsewhere and satisfy these protocols.
"""

from __future__ import annotations

from .base import ExternalTool, ToolCategory
from .dicom import DicomObject, DicomQuery, DicomReference, DICOMTool
from .email import EmailAttachment, EmailMessage, EmailReceipt, EmailTool
from .fhir import FhirQuery, FhirReference, FhirResource, FHIRTool
from .hl7 import Hl7Ack, Hl7Message, Hl7ParseResult, Hl7Segment, HL7Tool
from .ocr import OcrBlock, OcrImage, OcrResult, OCRTool
from .pdf import ExtractedText, PdfDocument, PDFTool, RenderedPage
from .supabase import (
    SupabaseMutation,
    SupabaseQuery,
    SupabaseResult,
    SupabaseTool,
)
from .voice import AudioClip, SpeechRequest, Transcript, VoiceTool

__all__ = [
    # base
    "ExternalTool",
    "ToolCategory",
    # tool contracts
    "SupabaseTool",
    "PDFTool",
    "OCRTool",
    "EmailTool",
    "VoiceTool",
    "FHIRTool",
    "HL7Tool",
    "DICOMTool",
    # supabase models
    "SupabaseQuery",
    "SupabaseMutation",
    "SupabaseResult",
    # pdf models
    "PdfDocument",
    "ExtractedText",
    "RenderedPage",
    # ocr models
    "OcrImage",
    "OcrBlock",
    "OcrResult",
    # email models
    "EmailAttachment",
    "EmailMessage",
    "EmailReceipt",
    # voice models
    "AudioClip",
    "Transcript",
    "SpeechRequest",
    # fhir models
    "FhirReference",
    "FhirResource",
    "FhirQuery",
    # hl7 models
    "Hl7Message",
    "Hl7Segment",
    "Hl7ParseResult",
    "Hl7Ack",
    # dicom models
    "DicomQuery",
    "DicomReference",
    "DicomObject",
]
