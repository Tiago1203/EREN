"""
PHASE 4 - EPIC 5: BM25 Module

Implementación de BM25 para búsqueda por keywords:
- BM25 Classic
- BM25L (para documentos cortos)
- BM25+ (variante)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import math
from collections import Counter


# BM25 parameters
DEFAULT_K1 = 1.5
DEFAULT_B = 0.75


class BaseBM25(ABC):
    """Clase base para BM25."""
    
    @abstractmethod
    def score(self, query: list[str], document: list[str]) -> float:
        """Calcula score BM25."""
        ...
    
    @abstractmethod
    def search(self, query: str, documents: list[dict]) -> list[tuple]:
        """Busca en documentos."""
        ...


class BM25Classic(BaseBM25):
    """BM25 clásico (Okapi BM25)."""
    
    def __init__(self, k1: float = DEFAULT_K1, b: float = DEFAULT_B):
        self.k1 = k1
        self.b = b
        self.avg_doc_len = 0.0
        self.doc_freqs: dict[str, int] = {}
        self.doc_lens: list[int] = []
        self.N = 0  # Total documents
    
    def index(self, documents: list[list[str]]) -> None:
        """Indexa documentos."""
        self.N = len(documents)
        self.doc_lens = []
        self.doc_freqs = Counter()
        total_len = 0
        
        for doc in documents:
            doc_len = len(doc)
            self.doc_lens.append(doc_len)
            total_len += doc_len
            
            # Count term frequencies
            unique_terms = set(doc)
            for term in unique_terms:
                self.doc_freqs[term] += 1
        
        self.avg_doc_len = total_len / self.N if self.N > 0 else 0
    
    def score(self, query: list[str], document: list[str]) -> float:
        """Calcula score BM25 para un documento."""
        if not query or not document or self.N == 0:
            return 0.0
        
        doc_len = len(document)
        doc_tf = Counter(document)
        
        score = 0.0
        
        for term in query:
            if term not in doc_tf:
                continue
            
            tf = doc_tf[term]
            df = self.doc_freqs.get(term, 0)
            
            if df == 0:
                continue
            
            # IDF
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
            
            # TF component
            tf_component = (tf * (self.k1 + 1)) / (
                tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
            )
            
            score += idf * tf_component
        
        return score
    
    def search(self, query: str, documents: list[dict]) -> list[tuple]:
        """Busca en documentos."""
        # Tokenize query
        query_terms = self._tokenize(query)
        
        # Index documents if not already indexed
        if self.N == 0:
            doc_texts = [self._tokenize(d.get("text", "")) for d in documents]
            self.index(doc_texts)
        
        # Score each document
        scores = []
        for i, doc in enumerate(documents):
            doc_text = self._tokenize(doc.get("text", ""))
            score = self.score(query_terms, doc_text)
            scores.append((doc.get("id", str(i)), doc, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[2], reverse=True)
        
        return scores
    
    def _tokenize(self, text: str) -> list[str]:
        """Tokeniza texto."""
        return text.lower().split()


class BM25L(BM25Classic):
    """BM25L para documentos cortos."""
    
    def score(self, query: list[str], document: list[str]) -> float:
        """Calcula score BM25L."""
        if not query or not document or self.N == 0:
            return 0.0
        
        doc_len = len(document)
        doc_tf = Counter(document)
        
        # BM25L uses different tf normalization
        delta = 0.5
        
        score = 0.0
        
        for term in query:
            if term not in doc_tf:
                continue
            
            tf = doc_tf[term]
            df = self.doc_freqs.get(term, 0)
            
            if df == 0:
                continue
            
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
            
            # BM25L tf normalization
            tf_component = (tf + delta) / (
                doc_len + delta
            )
            
            score += idf * tf_component
        
        return score


class BM25Plus(BM25Classic):
    """BM25+ - variante que evita score zero."""
    
    def score(self, query: list[str], document: list[str]) -> float:
        """Calcula score BM25+."""
        if not query or not document or self.N == 0:
            return 0.0
        
        doc_len = len(document)
        doc_tf = Counter(document)
        
        delta = 1.0
        
        score = 0.0
        
        for term in query:
            if term not in doc_tf:
                continue
            
            tf = doc_tf[term]
            df = self.doc_freqs.get(term, 0)
            
            if df == 0:
                continue
            
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
            
            # BM25+ adds delta to tf component
            tf_component = (tf * (self.k1 + 1)) / (
                tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
            ) + delta
            
            score += idf * tf_component
        
        return score


class BM25Searcher:
    """Wrapper para usar BM25 como searcher."""
    
    def __init__(
        self,
        variant: str = "classic",
        k1: float = DEFAULT_K1,
        b: float = DEFAULT_B,
    ):
        if variant == "bm25l":
            self.bm25 = BM25L(k1=k1, b=b)
        elif variant == "bm25+":
            self.bm25 = BM25Plus(k1=k1, b=b)
        else:
            self.bm25 = BM25Classic(k1=k1, b=b)
    
    def index_documents(self, documents: list[dict]) -> None:
        """Indexa documentos."""
        doc_texts = [self._tokenize(d.get("text", "")) for d in documents]
        self.bm25.index(doc_texts)
        self._documents = documents
    
    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Busca documentos."""
        results = self.bm25.search(query, self._documents or [])
        
        # Return top N
        return [
            {
                **doc,
                "score": score,
                "bm25_score": score,
            }
            for _, doc, score in results[:limit]
        ]
    
    def _tokenize(self, text: str) -> list[str]:
        """Tokeniza texto."""
        # Simple tokenization
        return text.lower().split()


__all__ = [
    "BaseBM25",
    "BM25Classic",
    "BM25L",
    "BM25Plus",
    "BM25Searcher",
    "DEFAULT_K1",
    "DEFAULT_B",
]
