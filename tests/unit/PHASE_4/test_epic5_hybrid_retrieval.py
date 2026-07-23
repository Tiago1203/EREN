"""Unit tests for EPIC 5: Hybrid Retrieval."""

import pytest
import asyncio


class TestEPIC5Imports:
    """Tests for EPIC 5 module imports."""

    def test_import_epic5(self):
        """Test EPIC 5 module imports."""
        from core.PHASE_4.epic5_hybrid_retrieval import (
            SemanticSearcher,
            ReciprocalRankFusion,
            BM25Classic,
        )
        assert SemanticSearcher is not None
        assert ReciprocalRankFusion is not None

    def test_import_search(self):
        """Test search module imports."""
        from core.PHASE_4.epic5_hybrid_retrieval.search import (
            SearchParams,
            VectorSearcher,
            KeywordSearcher,
        )
        assert SearchParams is not None
        assert VectorSearcher is not None

    def test_import_bm25(self):
        """Test bm25 module imports."""
        from core.PHASE_4.epic5_hybrid_retrieval.bm25 import (
            BM25Classic,
            BM25L,
            BM25Plus,
        )
        assert BM25Classic is not None
        assert BM25L is not None

    def test_import_fusion(self):
        """Test fusion module imports."""
        from core.PHASE_4.epic5_hybrid_retrieval.fusion import (
            ReciprocalRankFusion,
            WeightedAverageFusion,
            CombSUMFusion,
            CombMNZFusion,
        )
        assert ReciprocalRankFusion is not None
        assert WeightedAverageFusion is not None


class TestVectorSearcher:
    """Tests for VectorSearcher."""

    def test_searcher_creation(self):
        """Test VectorSearcher creation."""
        from core.PHASE_4.epic5_hybrid_retrieval import VectorSearcher
        
        searcher = VectorSearcher()
        assert searcher is not None

    def test_search_without_client(self):
        """Test search without vector client."""
        from core.PHASE_4.epic5_hybrid_retrieval import VectorSearcher, SearchParams
        import time
        
        searcher = VectorSearcher()
        params = SearchParams(query="test query", limit=10)
        
        response = asyncio.run(searcher.search(params))
        
        assert response.query == "test query"
        assert response.strategy_used == "vector"


class TestKeywordSearcher:
    """Tests for KeywordSearcher."""

    def test_searcher_creation(self):
        """Test KeywordSearcher creation."""
        from core.PHASE_4.epic5_hybrid_retrieval import KeywordSearcher
        
        searcher = KeywordSearcher()
        assert searcher is not None

    def test_index_and_search(self):
        """Test indexing and searching."""
        from core.PHASE_4.epic5_hybrid_retrieval import KeywordSearcher, SearchParams
        
        searcher = KeywordSearcher()
        
        # Index documents
        searcher.index_document("1", {"text": "heart failure treatment guidelines"})
        searcher.index_document("2", {"text": "diabetes management protocol"})
        
        # Search
        params = SearchParams(query="heart failure", limit=10)
        response = asyncio.run(searcher.search(params))
        
        assert response.query == "heart failure"
        assert len(response.results) >= 1

    def test_keyword_extraction(self):
        """Test keyword extraction."""
        from core.PHASE_4.epic5_hybrid_retrieval import KeywordSearcher
        
        searcher = KeywordSearcher()
        keywords = searcher._extract_keywords("Patient with heart failure symptoms")
        
        assert "heart" in keywords
        assert "failure" in keywords
        assert "symptoms" in keywords
        assert "patient" not in keywords  # Stopword


class TestBM25:
    """Tests for BM25."""

    def test_bm25_creation(self):
        """Test BM25 creation."""
        from core.PHASE_4.epic5_hybrid_retrieval import BM25Classic
        
        bm25 = BM25Classic()
        assert bm25 is not None

    def test_bm25_index(self):
        """Test BM25 indexing."""
        from core.PHASE_4.epic5_hybrid_retrieval import BM25Classic
        
        bm25 = BM25Classic()
        documents = [
            ["heart", "failure", "treatment"],
            ["diabetes", "management"],
            ["heart", "disease"],
        ]
        
        bm25.index(documents)
        
        assert bm25.N == 3
        assert bm25.doc_lens == [3, 2, 2]

    def test_bm25_score(self):
        """Test BM25 scoring."""
        from core.PHASE_4.epic5_hybrid_retrieval import BM25Classic
        
        bm25 = BM25Classic()
        documents = [
            ["heart", "failure", "treatment"],
            ["diabetes", "management"],
        ]
        
        bm25.index(documents)
        
        score = bm25.score(["heart"], ["heart", "failure", "treatment"])
        assert score > 0

    def test_bm25_search(self):
        """Test BM25 search."""
        from core.PHASE_4.epic5_hybrid_retrieval import BM25Classic
        
        bm25 = BM25Classic()
        documents = [
            {"id": "1", "text": "heart failure treatment"},
            {"id": "2", "text": "diabetes management"},
        ]
        
        results = bm25.search("heart failure", documents)
        
        assert len(results) == 2
        assert results[0][2] >= results[1][2]  # Sorted by score


class TestFusionMethods:
    """Tests for fusion methods."""

    def test_rrf_creation(self):
        """Test RRF creation."""
        from core.PHASE_4.epic5_hybrid_retrieval import ReciprocalRankFusion
        
        rrf = ReciprocalRankFusion(k=60)
        assert rrf.k == 60

    def test_rrf_fusion(self):
        """Test RRF fusion."""
        from core.PHASE_4.epic5_hybrid_retrieval import ReciprocalRankFusion, FusionResult
        
        rrf = ReciprocalRankFusion(k=60)
        
        list1 = [
            FusionResult(doc_id="1", fused_score=0.9, source_scores={"vector": 0.9}, source_ranks={"vector": 1}),
            FusionResult(doc_id="2", fused_score=0.8, source_scores={"vector": 0.8}, source_ranks={"vector": 2}),
        ]
        list2 = [
            FusionResult(doc_id="1", fused_score=0.7, source_scores={"keyword": 0.7}, source_ranks={"keyword": 1}),
            FusionResult(doc_id="3", fused_score=0.85, source_scores={"keyword": 0.85}, source_ranks={"keyword": 2}),
        ]
        
        fused = rrf.fuse([list1, list2])
        
        assert len(fused) == 3
        # Doc 1 should have highest score (in both lists)
        assert fused[0].doc_id == "1"

    def test_weighted_average(self):
        """Test weighted average fusion."""
        from core.PHASE_4.epic5_hybrid_retrieval import WeightedAverageFusion, FusionResult
        
        fusion = WeightedAverageFusion(
            weights={"vector": 0.7, "keyword": 0.3}
        )
        
        list1 = [FusionResult(doc_id="1", fused_score=1.0, source_scores={"vector": 1.0})]
        list2 = [FusionResult(doc_id="1", fused_score=0.5, source_scores={"keyword": 0.5})]
        
        fused = fusion.fuse([list1, list2])
        
        assert len(fused) == 1

    def test_combsum_fusion(self):
        """Test CombSUM fusion."""
        from core.PHASE_4.epic5_hybrid_retrieval import CombSUMFusion, FusionResult
        
        fusion = CombSUMFusion()
        
        # Use different docs with different scores
        list1 = [
            FusionResult(doc_id="1", fused_score=0.9, source_scores={"vector": 0.9}),
            FusionResult(doc_id="2", fused_score=0.5, source_scores={"vector": 0.5}),
        ]
        
        fused = fusion.fuse([list1])
        
        assert len(fused) == 2
        assert fused[0].doc_id == "1"


class TestSemanticSearcher:
    """Tests for SemanticSearcher."""

    def test_searcher_creation(self):
        """Test SemanticSearcher creation."""
        from core.PHASE_4.epic5_hybrid_retrieval import SemanticSearcher
        
        searcher = SemanticSearcher()
        assert searcher is not None

    def test_parallel_search(self):
        """Test parallel search execution."""
        from core.PHASE_4.epic5_hybrid_retrieval import SemanticSearcher, SearchParams
        
        searcher = SemanticSearcher()
        
        # Index documents in keyword searcher
        searcher.keyword_searcher.index_document("1", {"text": "heart failure"})
        searcher.keyword_searcher.index_document("2", {"text": "diabetes"})
        
        params = SearchParams(query="heart failure", limit=10)
        response = asyncio.run(searcher.search(params))
        
        assert response.query == "heart failure"
        assert response.strategy_used == "semantic"


class TestScoreNormalizer:
    """Tests for ScoreNormalizer."""

    def test_min_max_normalize(self):
        """Test min-max normalization."""
        from core.PHASE_4.epic5_hybrid_retrieval import ScoreNormalizer
        
        scores = [10, 20, 30, 40]
        normalized = ScoreNormalizer.min_max_normalize(scores)
        
        assert normalized[0] == 0.0
        assert normalized[3] == 1.0
        assert 0.0 <= normalized[1] <= 1.0

    def test_empty_scores(self):
        """Test empty scores."""
        from core.PHASE_4.epic5_hybrid_retrieval import ScoreNormalizer
        
        normalized = ScoreNormalizer.min_max_normalize([])
        assert normalized == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
