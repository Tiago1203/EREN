"""
PHASE 4 - EPIC 1: Extractors Module

Extractores especializados para documentos biomédicos:
- Table Extractor
- Figure Extractor
- Metadata Extractor
- Section Extractor
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import re
import uuid


@dataclass
class Table:
    """Tabla extraída de documento."""
    table_id: str
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    caption: str = ""
    page_number: int = 0
    position: int = 0
    confidence: float = 1.0
    format: str = "structured"  # structured, semi-structured, plain
    
    def to_markdown(self) -> str:
        """Convierte a markdown."""
        lines = []
        
        if self.caption:
            lines.append(f"**Table: {self.caption}**")
        
        if self.headers:
            lines.append("| " + " | ".join(self.headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(self.headers)) + " |")
        
        for row in self.rows:
            lines.append("| " + " | ".join(str(c) for c in row) + " |")
        
        return "\n".join(lines)
    
    def to_csv(self) -> str:
        """Convierte a CSV."""
        import csv
        from io import StringIO
        
        output = StringIO()
        if self.headers:
            output.write(",".join(self.headers) + "\n")
        
        for row in self.rows:
            output.write(",".join(str(c) for c in row) + "\n")
        
        return output.getvalue()


@dataclass
class Figure:
    """Figura extraída de documento."""
    figure_id: str
    caption: str = ""
    alt_text: str = ""
    page_number: int = 0
    position: int = 0
    width: int = 0
    height: int = 0
    format: str = ""  # png, jpg, svg
    referenced_in_text: bool = False
    source_reference: str = ""


@dataclass
class MedicalMetadata:
    """Metadata médica especializada."""
    # Bibliográfica
    pmid: str = ""
    pmcid: str = ""
    doi: str = ""
    isbn: str = ""
    
    # Clínica
    icd_codes: list[str] = field(default_factory=list)
    snomed_codes: list[str] = field(default_factory=list)
    loinc_codes: list[str] = field(default_factory=list)
    rxnorm_codes: list[str] = field(default_factory=list)
    
    # Publicación
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publication_date: str = ""
    epub_date: str = ""
    
    # Disciplina
    medical_specialty: str = ""
    subspecialties: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    msh_terms: list[str] = field(default_factory=list)  # MeSH terms
    
    # Regulación
    fda_approval_number: str = ""
    device_clearance: str = ""
    
    # Calidad
    peer_reviewed: bool = False
    impact_factor: float = 0.0
    citation_count: int = 0


@dataclass
class Section:
    """Sección de documento."""
    section_id: str
    title: str
    level: int  # 1 = h1, 2 = h2, etc
    content: str
    start_pos: int = 0
    end_pos: int = 0
    subsections: list[str] = field(default_factory=list)  # IDs de subsecciones
    is_appendix: bool = False
    is_reference: bool = False


@dataclass
class Attachment:
    """Archivo adjunto."""
    attachment_id: str
    filename: str
    content_type: str
    size_bytes: int = 0
    extracted_text: str = ""


class BaseExtractor(ABC):
    """Clase base para extractores."""
    
    @abstractmethod
    def extract(self, content: str, **kwargs) -> any:
        """Extrae información."""
        ...


class TableExtractor(BaseExtractor):
    """Extractor de tablas."""
    
    def __init__(self, strategy: str = "auto"):
        self.strategy = strategy
    
    def extract(self, content: str, **kwargs) -> list[Table]:
        """Extrae tablas del contenido."""
        tables = []
        page_number = kwargs.get('page_number', 0)
        
        # Detectar tablas en formato markdown
        md_tables = self._extract_markdown_tables(content, page_number)
        tables.extend(md_tables)
        
        # Detectar tablas en formato CSV
        csv_tables = self._extract_csv_tables(content, page_number)
        tables.extend(csv_tables)
        
        # Detectar tablas basadas en caracteres
        char_tables = self._extract_character_tables(content, page_number)
        tables.extend(char_tables)
        
        return tables
    
    def _extract_markdown_tables(self, content: str, page_number: int) -> list[Table]:
        """Extrae tablas markdown."""
        tables = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Buscar inicio de tabla markdown
            if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
                # Verificar que la segunda línea es separador
                separator = lines[i + 1].strip()
                if all(c in '-:| ' for c in separator):
                    table_id = str(uuid.uuid4())
                    headers = [h.strip() for h in line.split('|') if h.strip()]
                    
                    rows = []
                    j = i + 2
                    while j < len(lines) and '|' in lines[j]:
                        row = [c.strip() for c in lines[j].split('|') if c.strip()]
                        rows.append(row)
                        j += 1
                    
                    tables.append(Table(
                        table_id=table_id,
                        headers=headers,
                        rows=rows,
                        page_number=page_number,
                        position=i,
                        format="structured",
                    ))
                    
                    i = j
                    continue
            
            i += 1
        
        return tables
    
    def _extract_csv_tables(self, content: str, page_number: int) -> list[Table]:
        """Extrae tablas en formato CSV."""
        tables = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if ',' in line and not line.startswith('#'):
                # Posible CSV
                if self._looks_like_csv(line):
                    rows = []
                    for j in range(i, min(i + 20, len(lines))):
                        if ',' in lines[j]:
                            row = [c.strip() for c in lines[j].split(',')]
                            rows.append(row)
                        else:
                            break
                    
                    if len(rows) > 1:
                        tables.append(Table(
                            table_id=str(uuid.uuid4()),
                            headers=rows[0],
                            rows=rows[1:],
                            page_number=page_number,
                            position=i,
                            format="structured",
                        ))
                    break
        
        return tables
    
    def _extract_character_tables(self, content: str, page_number: int) -> list[Table]:
        """Extrae tablas basadas en alignment de caracteres."""
        # Placeholder - en producción usaría detección de bordes
        return []
    
    def _looks_like_csv(self, line: str) -> bool:
        """Verifica si la línea parece CSV."""
        comma_count = line.count(',')
        # Mínimo 2 comas para ser tabla
        return comma_count >= 2


class FigureExtractor(BaseExtractor):
    """Extractor de figuras."""
    
    def extract(self, content: str, **kwargs) -> list[Figure]:
        """Extrae figuras del contenido."""
        figures = []
        page_number = kwargs.get('page_number', 0)
        
        # Detectar referencias a figuras
        patterns = [
            r'Figure\s+(\d+[a-zA-Z]?)[:\.\s]',
            r'Fig\.\s+(\d+[a-zA-Z]?)[:\.\s]',
            r'\[Figure\s+(\d+[a-zA-Z]?)\]',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                figure_id = str(uuid.uuid4())
                figure_num = match.group(1)
                
                # Buscar caption cercana
                caption = self._find_nearby_caption(content, match.end(), 200)
                
                figures.append(Figure(
                    figure_id=figure_id,
                    caption=f"Figure {figure_num}: {caption}",
                    page_number=page_number,
                    referenced_in_text=True,
                ))
        
        return figures
    
    def _find_nearby_caption(self, content: str, pos: int, max_distance: int) -> str:
        """Busca caption cerca de la referencia."""
        end = min(pos + max_distance, len(content))
        snippet = content[pos:end]
        
        # Buscar fin de caption
        for end_marker in ['\n\n', '. ', '.\n']:
            marker_pos = snippet.find(end_marker)
            if marker_pos > 0 and marker_pos < 100:
                return snippet[:marker_pos].strip()
        
        return snippet[:100].strip()


class MetadataExtractor(BaseExtractor):
    """Extractor de metadata."""
    
    def extract(self, content: str, **kwargs) -> MedicalMetadata:
        """Extrae metadata médica."""
        metadata = MedicalMetadata()
        
        # Extraer del inicio del documento (antes de Abstract)
        header = content[:2000].lower()
        
        # DOI
        doi_match = re.search(r'doi[:\s]+(10\.\d{4,}/[^\s]+)', header)
        if doi_match:
            metadata.doi = doi_match.group(1)
        
        # PMID
        pmid_match = re.search(r'pmid[:\s]+(\d{6,})', header)
        if pmid_match:
            metadata.pmid = pmid_match.group(1)
        
        # PMCID
        pmcid_match = re.search(r'pmcid[:\s]+(PMC\d+)', header)
        if pmcid_match:
            metadata.pmcid = pmcid_match.group(1)
        
        # Códigos ICD
        icd_matches = re.findall(r'ICD[-\s]?(\d+\.?\d*)', header)
        metadata.icd_codes = list(set(icd_matches))
        
        # Keywords
        keywords_match = re.search(r'keywords?[:\s]+([^\n]+)', header)
        if keywords_match:
            keywords = re.split(r'[,;]', keywords_match.group(1))
            metadata.keywords = [k.strip() for k in keywords if k.strip()]
        
        return metadata


class SectionExtractor(BaseExtractor):
    """Extractor de secciones."""
    
    def extract(self, content: str, **kwargs) -> list[Section]:
        """Extrae secciones del documento."""
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        pos = 0
        
        for i, line in enumerate(lines):
            # Detectar headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            
            if header_match:
                # Guardar sección anterior
                if current_section:
                    current_section.content = '\n'.join(current_content)
                    current_section.end_pos = pos
                    sections.append(current_section)
                
                # Nueva sección
                level = len(header_match.group(1))
                title = header_match.group(2)
                
                current_section = Section(
                    section_id=str(uuid.uuid4()),
                    title=title,
                    level=level,
                    content='',
                    start_pos=pos,
                )
                current_content = []
            
            elif current_section:
                current_content.append(line)
            
            pos += len(line) + 1
        
        # Guardar última sección
        if current_section:
            current_section.content = '\n'.join(current_content)
            current_section.end_pos = pos
            sections.append(current_section)
        
        return sections


class LanguageDetector:
    """Detector de idioma."""
    
    # Common words in different languages
    STOPWORDS = {
        'en': {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'of', 'for', 'by'},
        'es': {'el', 'la', 'los', 'las', 'un', 'una', 'es', 'en', 'con', 'de', 'del', 'para', 'por', 'y', 'o'},
        'fr': {'le', 'la', 'les', 'un', 'une', 'est', 'en', 'avec', 'de', 'du', 'pour', 'par', 'et', 'ou'},
        'de': {'der', 'die', 'das', 'ein', 'eine', 'ist', 'in', 'mit', 'von', 'und', 'oder'},
        'pt': {'o', 'a', 'os', 'as', 'um', 'uma', 'é', 'em', 'com', 'de', 'do', 'da', 'para', 'e', 'ou'},
    }
    
    def detect(self, text: str) -> str:
        """Detecta idioma del texto."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return 'en'
        
        scores = {}
        for lang, stopwords in self.STOPWORDS.items():
            count = sum(1 for w in words if w in stopwords)
            scores[lang] = count / len(words)
        
        if max(scores.values()) < 0.01:
            return 'en'  # Default to English
        
        return max(scores, key=scores.get)


__all__ = [
    "Table",
    "Figure",
    "MedicalMetadata",
    "Section",
    "Attachment",
    "BaseExtractor",
    "TableExtractor",
    "FigureExtractor",
    "MetadataExtractor",
    "SectionExtractor",
    "LanguageDetector",
]
