"""
Evidence Bundle Module

Exports for bundling evidence with supporting and contradicting evidence.

ARCHITECTURE NOTE:
ComplianceStatus is imported from foundation (SINGLE SOURCE OF TRUTH).
EvidencePriority is a local enum specific to evidence bundling.
"""

from core.intelligence.evidence.bundle.evidence_bundle import (
    ComplianceStatus,
    EvidencePriority,
    RuleMatch,
    EvidenceSummary,
    EvidenceBundle,
    EvidenceBundleGenerator,
    EvidenceBundleManager,
)

__all__ = [
    "ComplianceStatus",
    "EvidencePriority",
    "RuleMatch",
    "EvidenceSummary",
    "EvidenceBundle",
    "EvidenceBundleGenerator",
    "EvidenceBundleManager",
]
