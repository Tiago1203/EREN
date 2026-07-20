"""
Versioning Module

Semantic versioning and release management.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ReleaseType(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


class Version(BaseModel):
    """Semantic version."""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @classmethod
    def parse(cls, version: str) -> "Version":
        """Parse version string."""
        parts = version.split(".")
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]),
            patch=int(parts[2])
        )


class ReleaseNotes(BaseModel):
    """Release notes."""
    version: str
    release_date: datetime
    release_type: ReleaseType
    title: str
    summary: str
    breaking_changes: List[str] = []
    new_features: List[str] = []
    bug_fixes: List[str] = []
    improvements: List[str] = []
    known_issues: List[str] = []
    upgrade_notes: List[str] = []


class ChangelogEntry(BaseModel):
    """Changelog entry."""
    version: str
    date: datetime
    changes: List[str]


class VersionManager:
    """Manages versioning."""
    
    CURRENT_VERSION = Version(major=1, minor=0, minor=0)  # Will be 1.0.0
    
    def __init__(self):
        self._changelog: List[ChangelogEntry] = []
    
    def get_current_version(self) -> str:
        """Get current version."""
        return str(self.CURRENT_VERSION)
    
    def bump_version(self, release_type: ReleaseType) -> Version:
        """Bump version based on release type."""
        if release_type == ReleaseType.MAJOR:
            self.CURRENT_VERSION.major += 1
            self.CURRENT_VERSION.minor = 0
            self.CURRENT_VERSION.patch = 0
        elif release_type == ReleaseType.MINOR:
            self.CURRENT_VERSION.minor += 1
            self.CURRENT_VERSION.patch = 0
        else:
            self.CURRENT_VERSION.patch += 1
        
        return self.CURRENT_VERSION
    
    def generate_release_notes(self, release_type: ReleaseType) -> ReleaseNotes:
        """Generate release notes."""
        new_version = self.bump_version(release_type)
        
        return ReleaseNotes(
            version=str(new_version),
            release_date=datetime.utcnow(),
            release_type=release_type,
            title=f"Version {new_version} Release",
            summary="Release with improvements and bug fixes.",
        )
    
    def add_changelog_entry(self, entry: ChangelogEntry):
        """Add changelog entry."""
        self._changelog.append(entry)
    
    def get_changelog(self, limit: int = 10) -> List[ChangelogEntry]:
        """Get changelog."""
        return sorted(
            self._changelog,
            key=lambda x: x.date,
            reverse=True
        )[:limit]


class ChangelogGenerator:
    """Generates changelogs."""
    
    @staticmethod
    def generate_from_commits(commits: List[Dict]) -> List[str]:
        """Generate changelog from commits."""
        changes = []
        
        for commit in commits:
            type_ = commit.get("type", "other")
            message = commit.get("message", "")
            
            if type_ == "feat":
                changes.append(f"✨ {message}")
            elif type_ == "fix":
                changes.append(f"🐛 {message}")
            elif type_ == "docs":
                changes.append(f"📚 {message}")
            elif type_ == "refactor":
                changes.append(f"♻️ {message}")
            elif type_ == "perf":
                changes.append(f"⚡️ {message}")
            else:
                changes.append(f"  {message}")
        
        return changes
