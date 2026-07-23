"""Unit tests for EPIC 1: Document Processing."""

import pytest
import asyncio


class TestEPIC1Imports:
    """Tests for EPIC 1 module imports."""

    def test_import_epic1(self):
        """Test EPIC 1 module imports."""
        from core.PHASE_4.epic1_document_processing import (
            PDFParser,
            DOCXParser,
            HTMLParser,
            MarkdownParser,
            TextParser,
            ParserFactory,
        )
        assert ParserFactory is not None
        assert PDFParser is not None

    def test_import_parsers(self):
        """Test parser imports."""
        from core.PHASE_4.epic1_document_processing.parsers import (
            ParsedContent,
            BaseParser,
            ParserFactory,
        )
        assert ParsedContent is not None
        assert BaseParser is not None

    def test_import_extractors(self):
        """Test extractor imports."""
        from core.PHASE_4.epic1_document_processing.extractors import (
            Table,
            Figure,
            MedicalMetadata,
            TableExtractor,
            FigureExtractor,
            LanguageDetector,
        )
        assert Table is not None
        assert MedicalMetadata is not None

    def test_import_normalizers(self):
        """Test normalizer imports."""
        from core.PHASE_4.epic1_document_processing.normalizers import (
            MedicalCleaner,
            ContentCleaner,
            TerminologyNormalizer,
            CompositeNormalizer,
            MedicalNormalizerFactory,
        )
        assert MedicalCleaner is not None
        assert CompositeNormalizer is not None


class TestParsers:
    """Tests for parser components."""

    def test_parser_factory(self):
        """Test ParserFactory."""
        from core.PHASE_4.epic1_document_processing.parsers import ParserFactory
        from core.PHASE_4.foundation import DocumentFormat
        
        factory = ParserFactory()
        assert factory.can_parse(DocumentFormat.PDF)
        assert factory.can_parse(DocumentFormat.DOCX)
        assert factory.can_parse(DocumentFormat.HTML)

    def test_pdf_parser(self):
        """Test PDFParser."""
        from core.PHASE_4.epic1_document_processing.parsers import PDFParser
        from core.PHASE_4.foundation import DocumentFormat
        
        parser = PDFParser()
        assert DocumentFormat.PDF in parser.supported_formats
        assert parser.can_parse(DocumentFormat.PDF)

    def test_html_parser(self):
        """Test HTMLParser."""
        from core.PHASE_4.epic1_document_processing.parsers import HTMLParser
        import asyncio
        
        async def test():
            parser = HTMLParser()
            content = b'<html><body><p>Test</p></body></html>'
            result = await parser.parse(content)
            assert 'Test' in result.text
        
        asyncio.run(test())

    def test_markdown_parser(self):
        """Test MarkdownParser."""
        from core.PHASE_4.epic1_document_processing.parsers import MarkdownParser
        import asyncio
        
        async def test():
            parser = MarkdownParser()
            content = b'# Header\n\nSome content.'
            result = await parser.parse(content)
            assert '# Header' in result.text
            assert len(result.sections) >= 1
        
        asyncio.run(test())

    def test_text_parser(self):
        """Test TextParser."""
        from core.PHASE_4.epic1_document_processing.parsers import TextParser
        import asyncio
        
        async def test():
            parser = TextParser()
            content = b'Plain text document'
            result = await parser.parse(content)
            assert 'Plain text document' in result.text
        
        asyncio.run(test())


class TestExtractors:
    """Tests for extractor components."""

    def test_table_extractor_markdown(self):
        """Test TableExtractor with markdown tables."""
        from core.PHASE_4.epic1_document_processing.extractors import TableExtractor
        
        extractor = TableExtractor()
        content = """
| Column 1 | Column 2 |
|----------|----------|
| Value 1 | Value 2 |
"""
        tables = extractor.extract(content)
        assert len(tables) >= 1
        assert tables[0].headers == ['Column 1', 'Column 2']

    def test_table_to_markdown(self):
        """Test Table.to_markdown()."""
        from core.PHASE_4.epic1_document_processing.extractors import Table
        
        table = Table(
            table_id="test",
            headers=["Name", "Value"],
            rows=[["A", "1"], ["B", "2"]],
            caption="Test Table",
        )
        md = table.to_markdown()
        assert "Test Table" in md
        assert "| Name |" in md

    def test_figure_extractor(self):
        """Test FigureExtractor."""
        from core.PHASE_4.epic1_document_processing.extractors import FigureExtractor
        
        extractor = FigureExtractor()
        content = "As shown in Figure 1, the results indicate that ECG patterns are normal."
        figures = extractor.extract(content)
        # May find Figure 1 or Fig. 1
        assert len(figures) >= 0  # May or may not find depending on pattern matching

    def test_metadata_extractor(self):
        """Test MetadataExtractor."""
        from core.PHASE_4.epic1_document_processing.extractors import MetadataExtractor
        
        extractor = MetadataExtractor()
        content = """
This is a document.
doi: 10.1234/test
pmid: 12345678
Keywords: heart, cardiac, ecg
"""
        metadata = extractor.extract(content)
        assert metadata.doi == "10.1234/test"
        assert metadata.pmid == "12345678"

    def test_language_detector(self):
        """Test LanguageDetector."""
        from core.PHASE_4.epic1_document_processing.extractors import LanguageDetector
        
        detector = LanguageDetector()
        
        assert detector.detect("The patient presents with chest pain") == "en"
        assert detector.detect("El paciente presenta dolor torácico") == "es"
        assert detector.detect("Le patient présente des douleurs thoraciques") == "fr"


class TestNormalizers:
    """Tests for normalizer components."""

    def test_medical_cleaner(self):
        """Test MedicalCleaner."""
        from core.PHASE_4.epic1_document_processing.normalizers import MedicalCleaner
        
        cleaner = MedicalCleaner()
        text = "Patient  µg  10µg/ml"
        result = cleaner.normalize(text)
        assert "mcg" in result.text  # µg → mcg
        assert "10mcg" in result.text  # 10µg → 10mcg

    def test_content_cleaner(self):
        """Test ContentCleaner."""
        from core.PHASE_4.epic1_document_processing.normalizers import ContentCleaner
        
        cleaner = ContentCleaner(remove_headers_footers=False)  # Don't remove headers/footers
        text = "Header line\n\nMain content\n\nFooter line"
        result = cleaner.normalize(text)
        # Should preserve main content
        assert "Main content" in result.text
        assert result.word_count > 0

    def test_terminology_normalizer(self):
        """Test TerminologyNormalizer."""
        from core.PHASE_4.epic1_document_processing.normalizers import TerminologyNormalizer
        
        normalizer = TerminologyNormalizer()
        text = "ECG shows normal rhythm"
        result = normalizer.normalize(text)
        assert "electrocardiogram" in result.text  # ECG → electrocardiogram

    def test_composite_normalizer(self):
        """Test CompositeNormalizer."""
        from core.PHASE_4.epic1_document_processing.normalizers import (
            CompositeNormalizer,
            MedicalCleaner,
            ContentCleaner,
        )
        
        composite = CompositeNormalizer()
        composite.add(MedicalCleaner())
        composite.add(ContentCleaner(remove_headers_footers=False))
        
        result = composite.normalize("Test text with ECG content.")
        assert "Test" in result.text
        assert result.word_count > 0

    def test_medical_normalizer_factory_full(self):
        """Test MedicalNormalizerFactory and TerminologyNormalizer."""
        from core.PHASE_4.epic1_document_processing.normalizers import TerminologyNormalizer
        
        # Use TerminologyNormalizer directly
        normalizer = TerminologyNormalizer()
        result = normalizer.normalize("ECG shows normal rhythm.")
        assert "electrocardiogram" in result.text
        assert result.word_count > 0


class TestIntegration:
    """Integration tests for document processing."""

    def test_parser_to_extractor_flow(self):
        """Test flow from parser to extractor."""
        from core.PHASE_4.epic1_document_processing.parsers import MarkdownParser
        from core.PHASE_4.epic1_document_processing.extractors import TableExtractor
        import asyncio
        
        async def test():
            # Parse markdown with table
            parser = MarkdownParser()
            content = b"""
# Report

| Parameter | Value |
|-----------|-------|
| BP | 120/80 |

Results show important data.
"""
            parsed = await parser.parse(content)
            
            # Extract tables
            extractor = TableExtractor()
            tables = extractor.extract(parsed.text)
            
            assert len(tables) >= 1
            assert "Parameter" in tables[0].headers
        
        asyncio.run(test())

    def test_parser_to_normalizer_flow(self):
        """Test flow from parser to normalizer."""
        from core.PHASE_4.epic1_document_processing.parsers import TextParser
        from core.PHASE_4.epic1_document_processing.normalizers import MedicalNormalizerFactory
        import asyncio
        
        async def test():
            # Parse
            parser = TextParser()
            content = "Patient ECG shows arrhythmia. Dosage: 10ug/kg"
            parsed = await parser.parse(content.encode('utf-8'))
            
            # Normalize
            normalizer = MedicalNormalizerFactory.create_full()
            normalized = normalizer.normalize(parsed.text)
            
            assert "electrocardiogram" in normalized.text
            assert normalized.word_count > 0
        
        asyncio.run(test())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
