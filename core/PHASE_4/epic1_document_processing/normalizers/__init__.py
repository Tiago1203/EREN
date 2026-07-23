"""
PHASE 4 - EPIC 1: Normalizers Module

Normalizadores para documentos biomédicos:
- Medical Cleaner
- Content Normalizer
- Structure Normalizer
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import re


@dataclass
class NormalizationResult:
    """Resultado de normalización."""
    text: str
    changes: list[str] = field(default_factory=list)
    word_count: int = 0
    char_count: int = 0


class BaseNormalizer(ABC):
    """Clase base para normalizadores."""
    
    @abstractmethod
    def normalize(self, text: str) -> NormalizationResult:
        """Normaliza el texto."""
        ...


class MedicalCleaner(BaseNormalizer):
    """Limpiador especializado para texto médico."""
    
    # Patrones de ruido médico
    MEDICAL_NOISE_PATTERNS = {
        # Whitespaces múltiples
        r'\s+': ' ',
        # Caracteres especiales problemáticos
        r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]': '',
        # Smart quotes
        r'[\u2018\u2019]': "'",
        r'[\u201c\u201d]': '"',
        r'[\u2013\u2014]': '-',
        # Caracteres de control
        r'\r\n': '\n',
        # Espacios en blanco al final de línea
        r' +\n': '\n',
    }
    
    # Símbolos médicos comunes
    SYMBOL_REPLACEMENTS = {
        'µg': 'mcg',  # Microgramos
        'µL': 'mcL',  # Microlitros
        '≤': '<=',
        '≥': '>=',
        '±': '+/-',
        '°C': 'C',
    }
    
    def normalize(self, text: str) -> NormalizationResult:
        """Limpia texto médico."""
        changes = []
        result = text
        
        # Aplicar patrones de ruido
        for pattern, replacement in self.MEDICAL_NOISE_PATTERNS.items():
            new_result = re.sub(pattern, replacement, result)
            if new_result != result:
                changes.append(f"Applied pattern: {pattern}")
                result = new_result
        
        # Reemplazar símbolos
        for symbol, replacement in self.SYMBOL_REPLACEMENTS.items():
            if symbol in result:
                result = result.replace(symbol, replacement)
                changes.append(f"Replaced symbol: {symbol} -> {replacement}")
        
        # Limpiar líneas vacías múltiples
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return NormalizationResult(
            text=result.strip(),
            changes=changes,
            word_count=len(result.split()),
            char_count=len(result),
        )


class ContentCleaner(BaseNormalizer):
    """Limpiador de contenido general."""
    
    def __init__(self, remove_headers_footers: bool = True):
        self.remove_headers_footers = remove_headers_footers
    
    def normalize(self, text: str) -> NormalizationResult:
        """Limpia contenido."""
        changes = []
        result = text
        
        # Remover headers y footers comunes
        if self.remove_headers_footers:
            result, removed = self._remove_headers_footers(result)
            if removed:
                changes.append("Removed headers/footers")
        
        # Normalizar puntuación
        result = self._normalize_punctuation(result)
        
        # Remover artifacts de OCR
        result = self._remove_ocr_artifacts(result)
        
        return NormalizationResult(
            text=result,
            changes=changes,
            word_count=len(result.split()),
            char_count=len(result),
        )
    
    def _remove_headers_footers(self, text: str) -> tuple:
        """Remueve headers y footers."""
        lines = text.split('\n')
        
        # Headers: primeras líneas cortas
        # Footers: últimas líneas cortas
        start = 0
        end = len(lines)
        
        # Detectar header
        for i, line in enumerate(lines[:5]):
            if len(line.strip()) < 30 and line.strip():
                start = i + 1
        
        # Detectar footer
        for i in range(len(lines) - 1, max(len(lines) - 6, 0), -1):
            if len(lines[i].strip()) < 30 and lines[i].strip():
                end = i
        
        cleaned = '\n'.join(lines[start:end])
        removed = (start > 0 or end < len(lines))
        
        return cleaned, removed
    
    def _normalize_punctuation(self, text: str) -> str:
        """Normaliza puntuación."""
        # Espacios antes de puntuación
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        # Espacios después de puntuación (excepto antes de mayúsculas)
        text = re.sub(r'([.,;:!?])(?=[A-Z0-9])', r'\1 ', text)
        return text
    
    def _remove_ocr_artifacts(self, text: str) -> str:
        """Remueve artifacts comunes de OCR."""
        # Caracteres aislados que parecen errores de OCR
        text = re.sub(r'\b[b-df-hj-np-tv-z]\b', '', text, flags=re.IGNORECASE)
        # Líneas con muy pocos caracteres
        lines = text.split('\n')
        cleaned_lines = [l for l in lines if len(l.strip()) > 2 or l.strip() == '']
        return '\n'.join(cleaned_lines)


class StructureNormalizer(BaseNormalizer):
    """Normalizador de estructura de documento."""
    
    def normalize(self, text: str) -> NormalizationResult:
        """Normaliza estructura."""
        changes = []
        result = text
        
        # Asegurar que hay espacio entre secciones
        result = re.sub(r'\n#', '\n\n#', result)
        result = re.sub(r'\n\n#', '\n\n#', result)
        
        # Normalizar headers
        lines = result.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Headers markdown
            if re.match(r'^#{1,6}\s', line):
                line = line.strip()
            
            normalized_lines.append(line)
        
        result = '\n'.join(normalized_lines)
        
        return NormalizationResult(
            text=result.strip(),
            changes=changes,
            word_count=len(result.split()),
            char_count=len(result),
        )


class TerminologyNormalizer(BaseNormalizer):
    """Normalizador de terminología médica."""
    
    # Mapeos de terminología
    TERMINOLOGY_MAPS = {
        # Abreviaturas comunes
        'bp': 'blood pressure',
        'hr': 'heart rate',
        'temp': 'temperature',
        'wt': 'weight',
        'ht': 'height',
        'bmi': 'body mass index',
        'ecg': 'electrocardiogram',
        'ekg': 'electrocardiogram',
        'ct': 'computed tomography',
        'mri': 'magnetic resonance imaging',
        'cbc': 'complete blood count',
        'wbc': 'white blood cell',
        'rbc': 'red blood cell',
        'mi': 'myocardial infarction',
        'chf': 'congestive heart failure',
        'copd': 'chronic obstructive pulmonary disease',
        'dm': 'diabetes mellitus',
        'htn': 'hypertension',
        'ckd': 'chronic kidney disease',
        'esrd': 'end-stage renal disease',
        'gi': 'gastrointestinal',
        'neuro': 'neurological',
        'pulm': 'pulmonary',
        'cv': 'cardiovascular',
        'renal': 'kidney',
        'hepatic': 'liver',
        
        # Plurales irregulares comunes
        'phenomena': 'phenomenon',
        'criteria': 'criterion',
        'bacteria': 'bacterium',
        'fungi': 'fungus',
        'lumina': 'lumen',
    }
    
    def __init__(self, expand_abbreviations: bool = True):
        self.expand_abbreviations = expand_abbreviations
    
    def normalize(self, text: str) -> NormalizationResult:
        """Normaliza terminología."""
        changes = []
        result = text
        
        if self.expand_abbreviations:
            for abbrev, full in self.TERMINOLOGY_MAPS.items():
                # Reemplazar solo si es una palabra completa
                pattern = r'\b' + re.escape(abbrev) + r'\b'
                new_result = re.sub(pattern, full, result, flags=re.IGNORECASE)
                if new_result != result:
                    changes.append(f"Expanded: {abbrev} -> {full}")
                    result = new_result
        
        return NormalizationResult(
            text=result,
            changes=changes,
            word_count=len(result.split()),
            char_count=len(result),
        )


class CompositeNormalizer:
    """Normalizador compuesto que aplica múltiples normalizadores."""
    
    def __init__(self):
        self.normalizers: list[BaseNormalizer] = []
    
    def add(self, normalizer: BaseNormalizer) -> 'CompositeNormalizer':
        """Agrega un normalizador."""
        self.normalizers.append(normalizer)
        return self
    
    def normalize(self, text: str) -> NormalizationResult:
        """Aplica todos los normalizadores."""
        all_changes = []
        result = text
        
        for normalizer in self.normalizers:
            normalized = normalizer.normalize(result)
            result = normalized.text
            all_changes.extend(normalized.changes)
        
        return NormalizationResult(
            text=result,
            changes=all_changes,
            word_count=len(result.split()),
            char_count=len(result),
        )


class MedicalNormalizerFactory:
    """Fábrica de normalizadores médicos."""
    
    @staticmethod
    def create_full() -> CompositeNormalizer:
        """Crea normalizador completo."""
        return (CompositeNormalizer()
            .add(MedicalCleaner())
            .add(ContentCleaner())
            .add(StructureNormalizer())
            .add(TerminologyNormalizer()))
    
    @staticmethod
    def create_light() -> CompositeNormalizer:
        """Crea normalizador ligero."""
        return (CompositeNormalizer()
            .add(MedicalCleaner())
            .add(ContentCleaner()))


__all__ = [
    "NormalizationResult",
    "BaseNormalizer",
    "MedicalCleaner",
    "ContentCleaner",
    "StructureNormalizer",
    "TerminologyNormalizer",
    "CompositeNormalizer",
    "MedicalNormalizerFactory",
]
