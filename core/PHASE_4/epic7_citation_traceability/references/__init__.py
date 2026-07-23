"""
PHASE 4 - EPIC 7: References Module

Gestión de referencias:
- Reference Manager
- DOI Resolver
- Reference Index
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib


class ReferenceStatus(str, Enum):
    """Estados de referencia."""
    PENDING = "pending"
    VERIFIED = "verified"
    INVALID = "invalid"
    DEPRECATED = "deprecated"


@dataclass
class Reference:
    """Referencia."""
    reference_id: str
    doi: str = ""
    pmid: str = ""
    pmcid: str = ""
    
    # Metadata
    title: str = ""
    authors: list[str] = field(default_factory=list)
    journal: str = ""
    publication_date: str = ""
    
    # Status
    status: ReferenceStatus = ReferenceStatus.PENDING
    verified_at: str = ""
    verified_by: str = ""
    
    # Links
    pubmed_url: str = ""
    doi_url: str = ""
    
    def get_pubmed_url(self) -> str:
        """Obtiene URL de PubMed."""
        if self.pmid:
            return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"
        return ""
    
    def get_doi_url(self) -> str:
        """Obtiene URL de DOI."""
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return ""


class BaseReferenceManager(ABC):
    """Clase base para gestión de referencias."""
    
    @abstractmethod
    async def add_reference(self, reference: Reference) -> bool:
        """Añade referencia."""
        ...
    
    @abstractmethod
    async def get_reference(self, reference_id: str) -> Reference | None:
        """Obtiene referencia."""
        ...
    
    @abstractmethod
    async def verify_reference(self, reference_id: str) -> bool:
        """Verifica referencia."""
        ...


class InMemoryReferenceManager(BaseReferenceManager):
    """Gestor de referencias en memoria."""
    
    def __init__(self):
        self._references: dict[str, Reference] = {}
    
    async def add_reference(self, reference: Reference) -> bool:
        """Añade referencia."""
        if reference.reference_id in self._references:
            return False
        
        self._references[reference.reference_id] = reference
        return True
    
    async def get_reference(self, reference_id: str) -> Reference | None:
        """Obtiene referencia."""
        return self._references.get(reference_id)
    
    async def verify_reference(self, reference_id: str) -> bool:
        """Verifica referencia."""
        reference = self._references.get(reference_id)
        if not reference:
            return False
        
        reference.status = ReferenceStatus.VERIFIED
        reference.verified_at = datetime.now().isoformat()
        return True
    
    async def list_all(self) -> list[Reference]:
        """Lista todas las referencias."""
        return list(self._references.values())


class DOIResolver:
    """Resolver de DOIs."""
    
    def __init__(self):
        self._cache: dict[str, dict] = {}
    
    async def resolve(self, doi: str) -> dict | None:
        """Resuelve DOI a metadata."""
        if not doi:
            return None
        
        # Check cache
        if doi in self._cache:
            return self._cache[doi]
        
        # In production, would call CrossRef API or PubMed
        # For now, return mock data
        try:
            metadata = await self._fetch_doi_metadata(doi)
            if metadata:
                self._cache[doi] = metadata
            return metadata
        except Exception:
            return None
    
    async def _fetch_doi_metadata(self, doi: str) -> dict | None:
        """Busca metadata de DOI."""
        # Mock implementation - in production would call API
        return {
            "doi": doi,
            "title": f"Article about {doi}",
            "authors": ["Author A", "Author B"],
            "journal": "Journal of Medicine",
            "year": "2024",
            "pmid": "",
            "pmcid": "",
        }


class PubMedResolver:
    """Resolver de PubMed."""
    
    def __init__(self):
        self._cache: dict[str, dict] = {}
    
    async def resolve(self, pmid: str) -> dict | None:
        """Resuelve PMID a metadata."""
        if not pmid:
            return None
        
        # Check cache
        if pmid in self._cache:
            return self._cache[pmid]
        
        try:
            metadata = await self._fetch_pmid_metadata(pmid)
            if metadata:
                self._cache[pmid] = metadata
            return metadata
        except Exception:
            return None
    
    async def _fetch_pmid_metadata(self, pmid: str) -> dict | None:
        """Busca metadata de PMID."""
        # Mock implementation
        return {
            "pmid": pmid,
            "title": f"Article {pmid}",
            "authors": ["Author A"],
            "journal": "Medical Journal",
            "year": "2023",
            "doi": "",
        }


class ReferenceIndexer:
    """Indexador de referencias."""
    
    def __init__(self):
        self._index: dict[str, list[str]] = {}  # term -> [reference_ids]
    
    def index(self, reference: Reference) -> None:
        """Indexa referencia."""
        # Index by title words
        title_words = reference.title.lower().split()
        for word in title_words:
            if len(word) > 3:  # Skip short words
                if word not in self._index:
                    self._index[word] = []
                if reference.reference_id not in self._index[word]:
                    self._index[word].append(reference.reference_id)
        
        # Index by DOI
        if reference.doi:
            self._index[f"doi:{reference.doi}"] = [reference.reference_id]
        
        # Index by PMID
        if reference.pmid:
            self._index[f"pmid:{reference.pmid}"] = [reference.reference_id]
    
    def search(self, query: str) -> list[str]:
        """Busca referencias por query."""
        query_lower = query.lower()
        query_words = query_lower.split()
        
        results = set()
        
        for word in query_words:
            if len(word) > 3 and word in self._index:
                results.update(self._index[word])
        
        return list(results)


__all__ = [
    "ReferenceStatus",
    "Reference",
    "BaseReferenceManager",
    "InMemoryReferenceManager",
    "DOIResolver",
    "PubMedResolver",
    "ReferenceIndexer",
]
