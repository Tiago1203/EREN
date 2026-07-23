"""Unit tests for EPIC 8: Knowledge Quality Engine."""

import pytest


class TestEPIC8Imports:
    """Tests for EPIC 8 module imports."""

    def test_import_epic8(self):
        """Test EPIC 8 module imports."""
        from core.PHASE_4.epic8_knowledge_quality import (
            ClinicalQualityAnalyzer,
            ClinicalBiasDetector,
            ClinicalRankingEngine,
        )
        assert ClinicalQualityAnalyzer is not None
        assert ClinicalBiasDetector is not None

    def test_import_quality(self):
        """Test quality module imports."""
        from core.PHASE_4.epic8_knowledge_quality.quality import (
            QualityLevel,
            QualityScore,
            ClinicalQualityAnalyzer,
        )
        assert QualityLevel is not None
        assert QualityScore is not None

    def test_import_bias(self):
        """Test bias module imports."""
        from core.PHASE_4.epic8_knowledge_quality.bias import (
            BiasType,
            BiasReport,
            ClinicalBiasDetector,
        )
        assert BiasType is not None
        assert BiasReport is not None

    def test_import_ranking(self):
        """Test ranking module imports."""
        from core.PHASE_4.epic8_knowledge_quality.ranking import (
            EvidenceRank,
            RankedEvidence,
            ClinicalRankingEngine,
        )
        assert EvidenceRank is not None
        assert RankedEvidence is not None


class TestQualityScore:
    """Tests for QualityScore."""

    def test_quality_score_excellent(self):
        """Test excellent quality score."""
        from core.PHASE_4.epic8_knowledge_quality.quality import QualityScore, QualityLevel
        
        score = QualityScore(overall=0.95)
        assert score.level == QualityLevel.EXCELLENT

    def test_quality_score_poor(self):
        """Test poor quality score."""
        from core.PHASE_4.epic8_knowledge_quality.quality import QualityScore, QualityLevel
        
        score = QualityScore(overall=0.2)
        assert score.level == QualityLevel.UNACCEPTABLE


class TestClinicalQualityAnalyzer:
    """Tests for ClinicalQualityAnalyzer."""

    def test_analyzer_creation(self):
        """Test analyzer creation."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalQualityAnalyzer
        
        analyzer = ClinicalQualityAnalyzer()
        assert analyzer is not None

    def test_analyze_peer_reviewed(self):
        """Test analyzing peer-reviewed source."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalQualityAnalyzer
        
        analyzer = ClinicalQualityAnalyzer()
        
        report = analyzer.analyze({
            "id": "src_1",
            "text": "Peer reviewed study...",
            "score": 0.9,
            "metadata": {
                "peer_reviewed": True,
                "title": "Study",
                "authors": ["Smith"],
                "date": "2024-01-01",
            }
        })
        
        assert report.source_id == "src_1"
        assert report.score.accuracy > 0.7
        assert report.is_acceptable is True

    def test_analyze_low_quality(self):
        """Test analyzing low quality source."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalQualityAnalyzer
        from core.PHASE_4.epic8_knowledge_quality.quality import QualityLevel
        
        analyzer = ClinicalQualityAnalyzer()
        
        report = analyzer.analyze({
            "id": "src_2",
            "text": "Low quality content...",
            "score": 0.1,  # Very low relevance
            "metadata": {}
        })
        
        # Check that there are warnings/issues
        assert len(report.warnings) > 0

    def test_currency_assessment(self):
        """Test currency assessment."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalQualityAnalyzer
        
        analyzer = ClinicalQualityAnalyzer()
        
        # Recent source
        report = analyzer.analyze({
            "id": "1",
            "text": "Recent study...",
            "score": 0.8,
            "metadata": {"date": "2025-01-01"}
        })
        
        assert report.score.currency > 0.8


class TestBiasDetector:
    """Tests for ClinicalBiasDetector."""

    def test_detector_creation(self):
        """Test detector creation."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalBiasDetector
        
        detector = ClinicalBiasDetector()
        assert detector is not None

    def test_detect_industry_bias(self):
        """Test detecting industry bias."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalBiasDetector
        from core.PHASE_4.epic8_knowledge_quality.bias import BiasType
        
        detector = ClinicalBiasDetector()
        
        report = detector.detect({
            "id": "src_1",
            "text": "Study funded by pharmaceutical company...",
            "metadata": {"funding": "PharmaCorp"}
        })
        
        assert len(report.indicators) > 0
        assert any(i.bias_type == BiasType.INDUSTRY for i in report.indicators)

    def test_detect_no_bias(self):
        """Test detecting no bias."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalBiasDetector
        
        detector = ClinicalBiasDetector()
        
        report = detector.detect({
            "id": "src_1",
            "text": "Standard academic study...",
            "metadata": {
                "funding": "National Institute of Health",
                "language": "en",
                "date": "2024-01-01",
            }
        })
        
        assert report.overall_severity.value == "none"
        assert report.is_flagged is False


class TestEvidenceRank:
    """Tests for EvidenceRank."""

    def test_evidence_rank_high(self):
        """Test high evidence rank."""
        from core.PHASE_4.epic8_knowledge_quality.ranking import EvidenceRank
        
        assert EvidenceRank.HIGH.value == "high"

    def test_evidence_rank_excluded(self):
        """Test excluded evidence rank."""
        from core.PHASE_4.epic8_knowledge_quality.ranking import EvidenceRank
        
        assert EvidenceRank.EXCLUDED.value == "excluded"


class TestRankingEngine:
    """Tests for ClinicalRankingEngine."""

    def test_ranker_creation(self):
        """Test ranker creation."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalRankingEngine
        
        ranker = ClinicalRankingEngine()
        assert ranker is not None

    def test_rank_evidence(self):
        """Test ranking evidence."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalRankingEngine
        from core.PHASE_4.epic8_knowledge_quality.ranking import EvidenceRank
        
        ranker = ClinicalRankingEngine()
        
        items = [
            {"id": "1", "text": "High quality...", "score": 0.9, "quality_score": 0.8},
            {"id": "2", "text": "Low quality...", "score": 0.5, "quality_score": 0.3},
        ]
        
        ranked = ranker.rank(items)
        
        assert len(ranked) == 2
        assert ranked[0].rank_position == 1
        assert ranked[0].final_score > ranked[1].final_score

    def test_rank_sorted_by_score(self):
        """Test ranking is sorted by final score."""
        from core.PHASE_4.epic8_knowledge_quality import ClinicalRankingEngine
        
        ranker = ClinicalRankingEngine()
        
        items = [
            {"id": "low", "text": "Low...", "score": 0.3, "quality_score": 0.2},
            {"id": "high", "text": "High...", "score": 0.9, "quality_score": 0.9},
        ]
        
        ranked = ranker.rank(items)
        
        assert ranked[0].source_id == "high"
        assert ranked[1].source_id == "low"


class TestDuplicateDetector:
    """Tests for DuplicateDetector."""

    def test_detector_creation(self):
        """Test detector creation."""
        from core.PHASE_4.epic8_knowledge_quality.ranking import DuplicateDetector
        
        detector = DuplicateDetector()
        assert detector is not None

    def test_find_same_doi(self):
        """Test finding duplicates with same DOI."""
        from core.PHASE_4.epic8_knowledge_quality.ranking import DuplicateDetector
        
        detector = DuplicateDetector()
        
        items = [
            {"id": "1", "text": "Study A...", "metadata": {"doi": "10.1234/test"}},
            {"id": "2", "text": "Study B...", "metadata": {"doi": "10.1234/test"}},
        ]
        
        duplicates = detector.find_duplicates(items)
        
        assert len(duplicates) == 1
        assert ("1", "2") in duplicates or ("2", "1") in duplicates

    def test_find_no_duplicates(self):
        """Test no duplicates found."""
        from core.PHASE_4.epic8_knowledge_quality.ranking import DuplicateDetector
        
        detector = DuplicateDetector()
        
        items = [
            {"id": "1", "text": "Study A...", "metadata": {"doi": "10.1234/a"}},
            {"id": "2", "text": "Study B...", "metadata": {"doi": "10.1234/b"}},
        ]
        
        duplicates = detector.find_duplicates(items)
        
        assert len(duplicates) == 0


class TestQualityReport:
    """Tests for QualityReport."""

    def test_report_acceptable(self):
        """Test acceptable quality report."""
        from core.PHASE_4.epic8_knowledge_quality.quality import QualityReport, QualityScore, QualityLevel
        
        report = QualityReport(
            source_id="src_1",
            score=QualityScore(overall=0.8, level=QualityLevel.GOOD),
        )
        
        assert report.is_acceptable is True

    def test_report_unacceptable(self):
        """Test unacceptable quality report."""
        from core.PHASE_4.epic8_knowledge_quality.quality import QualityReport, QualityScore, QualityLevel
        
        report = QualityReport(
            source_id="src_1",
            score=QualityScore(overall=0.2, level=QualityLevel.POOR),
        )
        
        assert report.is_acceptable is False


class TestBiasReport:
    """Tests for BiasReport."""

    def test_report_not_flagged(self):
        """Test non-flagged bias report."""
        from core.PHASE_4.epic8_knowledge_quality.bias import BiasReport, BiasSeverity
        
        report = BiasReport(
            source_id="src_1",
            indicators=[],
        )
        
        assert report.is_flagged is False
        assert report.overall_severity == BiasSeverity.NONE

    def test_report_flagged(self):
        """Test flagged bias report."""
        from core.PHASE_4.epic8_knowledge_quality.bias import BiasReport, BiasSeverity, BiasIndicator, BiasType
        
        report = BiasReport(
            source_id="src_1",
            indicators=[
                BiasIndicator(
                    bias_type=BiasType.INDUSTRY,
                    severity=BiasSeverity.HIGH,
                    description="Industry bias detected",
                    score=0.8,
                )
            ],
        )
        
        assert report.is_flagged is True
        assert report.overall_severity == BiasSeverity.HIGH


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
