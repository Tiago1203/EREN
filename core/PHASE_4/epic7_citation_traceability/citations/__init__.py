"""
PHASE 4 - EPIC 7: Citations Module

Generación de citas:
- Citation Builder
- Citation Formatters
- Citation Validator
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import re


class CitationStyle(str, Enum):
    """Estilos de citación."""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    VANCOUVER = "vancouver"
    AMA = "ama"
    NUMERIC = "numeric"


@dataclass
class Citation:
    """Citación."""
    citation_id: str
    source_id: str
    style: CitationStyle
    
    # Reference info
    title: str
    authors: list[str] = field(default_factory=list)
    publication_date: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    
    # Identifiers
    doi: str = ""
    pmid: str = ""
    pmcid: str = ""
    url: str = ""
    
    # Quality
    is_verified: bool = False
    verification_date: str = ""
    
    def format(self) -> str:
        """Formatea según estilo."""
        formatters = {
            CitationStyle.APA: self._format_apa,
            CitationStyle.VANCOUVER: self._format_vancouver,
            CitationStyle.NUMERIC: self._format_numeric,
            CitationStyle.AMA: self._format_ama,
            CitationStyle.MLA: self._format_mla,
            CitationStyle.CHICAGO: self._format_chicago,
        }
        
        formatter = formatters.get(self.style, self._format_apa)
        return formatter()
    
    def _format_apa(self) -> str:
        """Formato APA: Author, A. A. (Year). Title. Journal, Volume(Issue), Pages."""
        parts = []
        
        # Authors
        if self.authors:
            if len(self.authors) > 6:
                parts.append(f"{self.authors[0]} et al.")
            else:
                parts.append(", ".join(self.authors))
        
        # Year
        if self.publication_date:
            year = self.publication_date[:4] if len(self.publication_date) >= 4 else self.publication_date
            parts.append(f"({year}).")
        else:
            parts.append("(n.d.).")
        
        # Title
        parts.append(f"{self.title}.")
        
        # Journal
        if self.journal:
            journal_part = f"*{self.journal}*"
            if self.volume:
                journal_part += f", {self.volume}"
            if self.issue:
                journal_part += f"({self.issue})"
            if self.pages:
                journal_part += f", {self.pages}"
            parts.append(journal_part + ".")
        
        # DOI
        if self.doi:
            parts.append(f"https://doi.org/{self.doi}")
        
        return " ".join(parts)
    
    def _format_vancouver(self) -> str:
        """Formato Vancouver: Authors. Title. Journal. Year;Volume(Issue):Pages."""
        parts = []
        
        # Authors
        if self.authors:
            if len(self.authors) > 6:
                parts.append(f"{self.authors[0]}, et al.")
            else:
                parts.append(", ".join([a.split()[-1] for a in self.authors]))
        
        # Title
        parts.append(f"{self.title}.")
        
        # Journal
        if self.journal:
            journal_part = self.journal
            if self.volume:
                journal_part += f" {self.volume}"
            if self.issue:
                journal_part += f"({self.issue})"
            if self.pages:
                journal_part += f":{self.pages}"
            parts.append(journal_part + ".")
        
        # Year
        if self.publication_date:
            year = self.publication_date[:4]
            parts.append(f"{year}.")
        
        # DOI
        if self.doi:
            parts.append(f"doi:{self.doi}")
        
        return " ".join(parts)
    
    def _format_numeric(self) -> str:
        """Formato Numérico: [1] Authors. Title. Journal. Year."""
        parts = []
        
        # Authors
        if self.authors:
            parts.append(f"[{self.citation_id}] {', '.join(self.authors[:3])}")
            if len(self.authors) > 3:
                parts[-1] += ", et al."
        
        # Title
        parts.append(f"{self.title}.")
        
        # Journal
        if self.journal:
            journal_part = self.journal
            if self.volume:
                journal_part += f" {self.volume}"
            if self.publication_date:
                year = self.publication_date[:4]
                journal_part += f" ({year})"
            parts.append(journal_part + ".")
        
        return " ".join(parts)
    
    def _format_ama(self) -> str:
        """Formato AMA: Authors. Title. Journal. Year;Volume(Issue):Pages."""
        return self._format_vancouver()  # Similar to Vancouver
    
    def _format_mla(self) -> str:
        """Formato MLA: Authors. "Title." Journal, vol. X, no. Y, Year, pp. Z-Z."""
        parts = []
        
        # Authors
        if self.authors:
            parts.append(", ".join(self.authors) + ".")
        
        # Title
        parts.append(f'"{self.title}."')
        
        # Journal
        if self.journal:
            journal_part = f"*{self.journal}*"
            if self.volume:
                journal_part += f", vol. {self.volume}"
            if self.issue:
                journal_part += f", no. {self.issue}"
            if self.publication_date:
                year = self.publication_date[:4]
                journal_part += f", {year}"
            if self.pages:
                journal_part += f", pp. {self.pages}"
            parts.append(journal_part + ".")
        
        return " ".join(parts)
    
    def _format_chicago(self) -> str:
        """Formato Chicago: Author. "Title." Journal Volume, no. Issue (Year): Pages."""
        parts = []
        
        # Authors
        if self.authors:
            parts.append(", ".join(self.authors) + ".")
        
        # Title
        parts.append(f'"{self.title}."')
        
        # Journal
        if self.journal:
            journal_part = f"*{self.journal}*"
            if self.volume:
                journal_part += f" {self.volume}"
            if self.issue:
                journal_part += f", no. {self.issue}"
            if self.publication_date:
                year = self.publication_date[:4]
                journal_part += f" ({year})"
            if self.pages:
                journal_part += f": {self.pages}"
            parts.append(journal_part + ".")
        
        return " ".join(parts)


class BaseCitationBuilder(ABC):
    """Clase base para builders de citación."""
    
    @abstractmethod
    def build(self, evidence_item: dict) -> Citation:
        """Construye citación."""
        ...


class ClinicalCitationBuilder(BaseCitationBuilder):
    """Builder de citaciones clínicas."""
    
    def __init__(self, style: CitationStyle = CitationStyle.APA):
        self.style = style
    
    def build(self, evidence_item: dict) -> Citation:
        """Construye citación desde evidence item."""
        import uuid
        
        metadata = evidence_item.get("metadata", {})
        
        return Citation(
            citation_id=str(uuid.uuid4())[:8],
            source_id=evidence_item.get("id", "unknown"),
            style=self.style,
            title=metadata.get("title", evidence_item.get("text", "")[:100]),
            authors=metadata.get("authors", []),
            publication_date=metadata.get("date", metadata.get("publication_date", "")),
            journal=metadata.get("journal", metadata.get("source", "")),
            volume=metadata.get("volume", ""),
            issue=metadata.get("issue", ""),
            pages=metadata.get("pages", ""),
            doi=metadata.get("doi", ""),
            pmid=metadata.get("pmid", ""),
            pmcid=metadata.get("pmcid", ""),
            url=metadata.get("url", ""),
        )


class CitationValidator:
    """Validador de citaciones."""
    
    def validate(self, citation: Citation) -> dict:
        """Valida citación."""
        issues = []
        
        # Check required fields
        if not citation.title:
            issues.append("Missing title")
        
        if not citation.authors:
            issues.append("Missing authors")
        
        # Validate DOI format
        if citation.doi:
            if not re.match(r"^10\.\d{4,}/", citation.doi):
                issues.append("Invalid DOI format")
        
        # Validate PMID format
        if citation.pmid:
            if not citation.pmid.isdigit() or len(citation.pmid) not in (7, 8):
                issues.append("Invalid PMID format")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "citation_id": citation.citation_id,
        }


__all__ = [
    "CitationStyle",
    "Citation",
    "BaseCitationBuilder",
    "ClinicalCitationBuilder",
    "CitationValidator",
]
