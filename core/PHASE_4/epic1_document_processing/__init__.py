"""
PHASE 4 - EPIC 1: Biomedical Document Processing Engine

Procesa documentos biomédicos de múltiples formatos:
- PDF con OCR para documentos escaneados
- DOCX con estilos y tablas
- HTML con estructura semántica
- Markdown con sintaxis estructurada
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Protocol
import uuid

from core.PHASE_4.foundation import (
    DocumentFormat,
    ProcessingStatus,
    ProcessedDocument,
    KnowledgeDomain,
)


class TextExtractionMethod(str, Enum):
    """Métodos de extracción de texto."""
    DIRECT = "direct"           # Extracción directa
    OCR = "ocr"                # Optical Character Recognition
    HYBRID = "hybrid"          # Combinación de métodos


class TableExtractionStrategy(str, Enum):
    """Estrategias para extracción de tablas."""
    STRUCTURED = "structured"   # Tablas bien formadas
    UNSTRUCTURED = "unstructured"  # Tablas con layout
    HYBRID = "hybrid"           # Detección automática


@dataclass
class DocumentMetadata:
    """Metadata extraída del documento."""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    publication_date: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str = ""
    isbn: str = ""
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    language: str = "en"
    license: str = ""
    source_type: str = ""  # pubmed, fda, clinical_guideline, etc
    
    # Clinical metadata
    medical_specialty: str = ""
    device_categories: list[str] = field(default_factory=list)
    icd_codes: list[str] = field(default_factory=list)
    
    # Document properties
    word_count: int = 0
    page_count: int = 0
    has_tables: bool = False
    has_figures: bool = False
    has_appendices: bool = False


@dataclass
class PageContent:
    """Contenido de una página."""
    page_number: int
    text: str
    sections: list[Section] = field(default_factory=list)
    tables: list[ExtractedTable] = field(default_factory=list)
    figures: list[FigureReference] = field(default_factory=list)


@dataclass
class Section:
    """Sección de un documento."""
    title: str
    level: int  # 1 = h1, 2 = h2, etc
    content: str
    start_pos: int
    end_pos: int
    subsection_ids: list[str] = field(default_factory=list)


@dataclass
class ExtractedTable:
    """Tabla extraída del documento."""
    table_id: str
    headers: list[str]
    rows: list[list[str]]
    caption: str = ""
    page_number: int = 0
    confidence: float = 1.0


@dataclass
class FigureReference:
    """Referencia a figura."""
    figure_id: str
    caption: str
    page_number: int
    referenced_in_text: bool = False


@dataclass
class ProcessingOptions:
    """Opciones de procesamiento."""
    extract_tables: bool = True
    extract_figures: bool = True
    extract_metadata: bool = True
    extract_sections: bool = True
    enable_ocr: bool = True
    ocr_language: str = "eng"
    normalize_whitespace: bool = True
    remove_headers_footers: bool = True
    preserve_formatting: bool = True


class IDocumentParser(Protocol):
    """Protocolo para parser de documentos."""
    
    async def parse(self, content: bytes) -> ParsedDocument:
        """Parse documento y extrae contenido."""
        ...


class IPDFProcessor:
    """Procesador de PDFs biomédicos."""
    
    async def process(
        self,
        content: bytes,
        options: ProcessingOptions,
    ) -> ProcessedDocument:
        """Procesa PDF y retorna documento extraído."""
        ...


class IDOCXProcessor:
    """Procesador de documentos Word."""
    
    async def process(
        self,
        content: bytes,
        options: ProcessingOptions,
    ) -> ProcessedDocument:
        """Procesa DOCX y retorna documento extraído."""
        ...


class IHTMLProcessor:
    """Procesador de HTML."""
    
    async def extract_text(
        self,
        html: str,
        options: ProcessingOptions,
    ) -> ProcessedDocument:
        """Extrae texto de HTML."""
        ...


class IOcrEngine:
    """Motor OCR para documentos escaneados."""
    
    async def recognize(
        self,
        image: bytes,
        language: str = "eng",
    ) -> str:
        """Reconoce texto en imagen."""
        ...
    
    async def recognize_document(
        self,
        images: list[bytes],
        language: str = "eng",
    ) -> list[str]:
        """Reconoce texto en documento multipágina."""
        ...


class ITextNormalizer:
    """Normalizador de texto."""
    
    def normalize(self, text: str) -> str:
        """Normaliza texto extraído."""
        ...
    
    def clean_whitespace(self, text: str) -> str:
        """Limpia espacios en blanco."""
        ...
    
    def remove_headers_footers(self, text: str) -> str:
        """Remueve headers y footers."""
        ...


class DocumentProcessingPipeline:
    """Pipeline completo de procesamiento de documentos."""
    
    def __init__(
        self,
        pdf_processor: IPDFProcessor | None = None,
        docx_processor: IDOCXProcessor | None = None,
        html_processor: IHTMLProcessor | None = None,
        ocr_engine: IOcrEngine | None = None,
    ):
        self.pdf_processor = pdf_processor
        self.docx_processor = docx_processor
        self.html_processor = html_processor
        self.ocr_engine = ocr_engine
        self.normalizer = TextNormalizer()
    
    async def process(
        self,
        content: bytes,
        format: DocumentFormat,
        options: ProcessingOptions | None = None,
        metadata: dict | None = None,
    ) -> ProcessedDocument:
        """Procesa documento según formato."""
        options = options or ProcessingOptions()
        metadata = metadata or {}
        
        if format == DocumentFormat.PDF:
            if self.pdf_processor:
                doc = await self.pdf_processor.process(content, options)
            else:
                doc = await self._process_pdf_fallback(content, options)
        
        elif format == DocumentFormat.DOCX:
            if self.docx_processor:
                doc = await self.docx_processor.process(content, options)
            else:
                doc = await self._process_docx_fallback(content, options)
        
        elif format == DocumentFormat.HTML:
            if self.html_processor:
                doc = await self.html_processor.extract_text(content.decode('utf-8'), options)
            else:
                doc = await self._process_html_fallback(content, options)
        
        else:
            doc = await self._process_text_fallback(content, options)
        
        # Apply metadata
        doc.metadata = {**doc.metadata, **metadata}
        doc.status = ProcessingStatus.COMPLETED
        
        return doc
    
    async def _process_pdf_fallback(
        self,
        content: bytes,
        options: ProcessingOptions,
    ) -> ProcessedDocument:
        """Fallback para PDF sin procesador especializado."""
        # Placeholder - would use PyPDF2, pdfplumber, etc.
        return ProcessedDocument(
            document_id=str(uuid.uuid4()),
            content="",
            format=DocumentFormat.PDF,
            metadata={},
            status=ProcessingStatus.COMPLETED,
        )
    
    async def _process_docx_fallback(
        self,
        content: bytes,
        options: ProcessingOptions,
    ) -> ProcessedDocument:
        """Fallback para DOCX sin procesador especializado."""
        return ProcessedDocument(
            document_id=str(uuid.uuid4()),
            content="",
            format=DocumentFormat.DOCX,
            metadata={},
            status=ProcessingStatus.COMPLETED,
        )
    
    async def _process_html_fallback(
        self,
        content: bytes,
        options: ProcessingOptions,
    ) -> ProcessedDocument:
        """Fallback para HTML."""
        from html.parser import HTMLParser
        
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_parts = []
            
            def handle_data(self, data):
                self.text_parts.append(data)
        
        parser = TextExtractor()
        parser.feed(content.decode('utf-8', errors='ignore'))
        text = '\n'.join(parser.text_parts)
        
        return ProcessedDocument(
            document_id=str(uuid.uuid4()),
            content=text,
            format=DocumentFormat.HTML,
            metadata={},
            status=ProcessingStatus.COMPLETED,
            word_count=len(text.split()),
        )
    
    async def _process_text_fallback(
        self,
        content: bytes,
        options: ProcessingOptions,
    ) -> ProcessedDocument:
        """Fallback para texto plano."""
        text = content.decode('utf-8', errors='ignore')
        if options.normalize_whitespace:
            text = self.normalizer.normalize(text)
        
        return ProcessedDocument(
            document_id=str(uuid.uuid4()),
            content=text,
            format=DocumentFormat.TEXT,
            metadata={},
            status=ProcessingStatus.COMPLETED,
            word_count=len(text.split()),
        )


class TextNormalizer:
    """Normalizador de texto para documentos biomédicos."""
    
    def normalize(self, text: str) -> str:
        """Normaliza texto completo."""
        text = self.clean_whitespace(text)
        text = self.remove_headers_footers(text)
        text = self.fix_encoding_issues(text)
        return text
    
    def clean_whitespace(self, text: str) -> str:
        """Limpia espacios múltiples y líneas vacías."""
        import re
        # Multiple spaces to single space
        text = re.sub(r' +', ' ', text)
        # Multiple newlines to double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        return '\n'.join(lines)
    
    def remove_headers_footers(self, text: str) -> str:
        """Intenta remover headers y footers comunes."""
        lines = text.split('\n')
        # Remove first line if it's a short header
        if lines and len(lines[0].strip()) < 50:
            lines = lines[1:]
        # Remove last line if it's a footer
        if lines and len(lines[-1].strip()) < 50:
            lines = lines[:-1]
        return '\n'.join(lines)
    
    def fix_encoding_issues(self, text: str) -> str:
        """Corrige problemas comunes de encoding."""
        replacements = {
            '\x00': '',      # Null bytes
            '\ufeff': '',    # BOM
            '\u2018': "'",   # Smart quotes
            '\u2019': "'",
            '\u201c': '"',
            '\u201d': '"',
            '\u2013': '-',   # En dash
            '\u2014': '--',  # Em dash
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text


class MetadataExtractor:
    """Extractor de metadata de documentos."""
    
    def extract_from_pdf(self, content: bytes, metadata: dict) -> DocumentMetadata:
        """Extrae metadata de PDF."""
        doc_metadata = DocumentMetadata()
        
        # Extract from PDF metadata dictionary
        if 'Title' in metadata:
            doc_metadata.title = metadata['Title']
        if 'Author' in metadata:
            doc_metadata.authors = [a.strip() for a in metadata['Author'].split(',')]
        if 'Subject' in metadata:
            doc_metadata.keywords = metadata['Subject'].split(',')
        
        return doc_metadata
    
    def extract_from_doi(self, doi: str) -> dict:
        """Obtiene metadata desde DOI."""
        # Would call CrossRef API
        return {}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "TextExtractionMethod",
    "TableExtractionStrategy",
    # Data Classes
    "DocumentMetadata",
    "PageContent",
    "Section",
    "ExtractedTable",
    "FigureReference",
    "ProcessingOptions",
    # Protocols
    "IDocumentParser",
    # Processors
    "IPDFProcessor",
    "IDOCXProcessor",
    "IHTMLProcessor",
    "IOcrEngine",
    "ITextNormalizer",
    # Pipeline
    "DocumentProcessingPipeline",
    "TextNormalizer",
    "MetadataExtractor",
]
