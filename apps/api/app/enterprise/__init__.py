"""
EREN Enterprise Module

Licensing, Versioning, Support, and Enterprise Features.
"""
from .licensing import LicenseManager, LicenseValidator, FeatureFlags
from .versioning import VersionManager, ReleaseNotes, ChangelogGenerator
from .support import SupportManager, SLAManager, EscalationMatrix

__all__ = [
    # Licensing
    "LicenseManager",
    "LicenseValidator",
    "FeatureFlags",
    # Versioning
    "VersionManager",
    "ReleaseNotes",
    "ChangelogGenerator",
    # Support
    "SupportManager",
    "SLAManager",
    "EscalationMatrix",
]
__version__ = "1.0.0"
