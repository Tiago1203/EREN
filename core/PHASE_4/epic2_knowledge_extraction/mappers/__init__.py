"""
PHASE 4 - EPIC 2: Mappers Module

Mapeadores de terminología biomédica:
- SNOMED Mapper
- UMLS Mapper
- MeSH Mapper
- ICD Mapper
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class OntologyReference:
    """Referencia a ontología médica."""
    reference_id: str
    ontology: str  # SNOMED, UMLS, MeSH, ICD10
    code: str
    display_name: str
    synonyms: list[str] = field(default_factory=list)
    definition: str = ""
    hierarchy: list[str] = field(default_factory=list)  # Path to root


@dataclass
class MappingResult:
    """Resultado de mapeo."""
    original_term: str
    ontology: str
    references: list[OntologyReference] = field(default_factory=list)
    best_match: Optional[OntologyReference] = None
    confidence: float = 0.0
    mapped: bool = False


class BaseOntologyMapper(ABC):
    """Clase base para mapeadores de ontologías."""
    
    @property
    @abstractmethod
    def ontology_name(self) -> str:
        """Retorna nombre de la ontología."""
        ...
    
    @abstractmethod
    async def map_term(self, term: str) -> MappingResult:
        """Mapea un término a la ontología."""
        ...
    
    @abstractmethod
    async def get_details(self, code: str) -> Optional[OntologyReference]:
        """Obtiene detalles de un código."""
        ...


class SNOMEDMapper(BaseOntologyMapper):
    """Mapper para SNOMED CT."""
    
    # Base de conocimiento SNOMED simplificada
    SNOMED_BASE = {
        "heart failure": {
            "code": "84114007",
            "display": "Heart failure (disorder)",
            "synonyms": ["cardiac failure", "CHF"],
            "hierarchy": ["Clinical finding", "Disease"],
        },
        "myocardial infarction": {
            "code": "22298006",
            "display": "Myocardial infarction (disorder)",
            "synonyms": ["MI", "heart attack"],
            "hierarchy": ["Clinical finding", "Disease"],
        },
        "hypertension": {
            "code": "38341003",
            "display": "Hypertensive disorder (disorder)",
            "synonyms": ["high blood pressure", "HTN"],
            "hierarchy": ["Clinical finding", "Disease"],
        },
        "diabetes": {
            "code": "73211009",
            "display": "Diabetes mellitus (disorder)",
            "synonyms": ["DM", "diabetes"],
            "hierarchy": ["Clinical finding", "Disease"],
        },
        "infusion pump": {
            "code": "706182007",
            "display": "Infusion pump (physical object)",
            "synonyms": ["pump", "IV pump"],
            "hierarchy": ["Physical object", "Device"],
        },
        "ventilator": {
            "code": "425498006",
            "display": "Ventilator (physical object)",
            "synonyms": ["respirator", "breathing machine"],
            "hierarchy": ["Physical object", "Device"],
        },
        "defibrillator": {
            "code": "448923006",
            "display": "Defibrillator (physical object)",
            "synonyms": ["AED", "ICD"],
            "hierarchy": ["Physical object", "Device"],
        },
        "aspirin": {
            "code": "387458008",
            "display": "Aspirin (substance)",
            "synonyms": ["acetylsalicylic acid", "ASA"],
            "hierarchy": ["Substance", "Pharmaceutical / biologic product"],
        },
        "lisinopril": {
            "code": "314076006",
            "display": "Lisinopril (substance)",
            "synonyms": ["ACE inhibitor"],
            "hierarchy": ["Substance", "Pharmaceutical / biologic product"],
        },
        "metformin": {
            "code": "860975",
            "display": "Metformin (substance)",
            "synonyms": ["biguanide"],
            "hierarchy": ["Substance", "Pharmaceutical / biologic product"],
        },
    }
    
    @property
    def ontology_name(self) -> str:
        return "SNOMED-CT"
    
    async def map_term(self, term: str) -> MappingResult:
        """Mapea término a SNOMED."""
        term_lower = term.lower()
        
        # Buscar en base local
        if term_lower in self.SNOMED_BASE:
            data = self.SNOMED_BASE[term_lower]
            ref = OntologyReference(
                reference_id=str(uuid.uuid4()),
                ontology=self.ontology_name,
                code=data["code"],
                display_name=data["display"],
                synonyms=data["synonyms"],
                hierarchy=data["hierarchy"],
            )
            return MappingResult(
                original_term=term,
                ontology=self.ontology_name,
                references=[ref],
                best_match=ref,
                confidence=0.95,
                mapped=True,
            )
        
        # Buscar por sinónimo
        for key, data in self.SNOMED_BASE.items():
            if term_lower in data["synonyms"] or any(term_lower in s for s in data["synonyms"]):
                ref = OntologyReference(
                    reference_id=str(uuid.uuid4()),
                    ontology=self.ontology_name,
                    code=data["code"],
                    display_name=data["display"],
                    synonyms=data["synonyms"],
                    hierarchy=data["hierarchy"],
                )
                return MappingResult(
                    original_term=term,
                    ontology=self.ontology_name,
                    references=[ref],
                    best_match=ref,
                    confidence=0.85,
                    mapped=True,
                )
        
        # No encontrado
        return MappingResult(
            original_term=term,
            ontology=self.ontology_name,
            mapped=False,
        )
    
    async def get_details(self, code: str) -> Optional[OntologyReference]:
        """Obtiene detalles de código SNOMED."""
        for key, data in self.SNOMED_BASE.items():
            if data["code"] == code:
                return OntologyReference(
                    reference_id=str(uuid.uuid4()),
                    ontology=self.ontology_name,
                    code=code,
                    display_name=data["display"],
                    synonyms=data["synonyms"],
                    hierarchy=data["hierarchy"],
                )
        return None


class UMLSMapper(BaseOntologyMapper):
    """Mapper para UMLS."""
    
    UMLS_BASE = {
        "cardiac": {
            "cui": "C0018799",
            "display": "Heart",
            "semantic_types": ["Body Part, Organ, or Organ Component"],
        },
        "pulmonary": {
            "cui": "C0024117",
            "display": "Lung",
            "semantic_types": ["Body Part, Organ, or Organ Component"],
        },
        "renal": {
            "cui": "C0022675",
            "display": "Kidney",
            "semantic_types": ["Body Part, Organ, or Organ Component"],
        },
    }
    
    @property
    def ontology_name(self) -> str:
        return "UMLS"
    
    async def map_term(self, term: str) -> MappingResult:
        """Mapea término a UMLS."""
        term_lower = term.lower()
        
        if term_lower in self.UMLS_BASE:
            data = self.UMLS_BASE[term_lower]
            ref = OntologyReference(
                reference_id=str(uuid.uuid4()),
                ontology=self.ontology_name,
                code=data["cui"],
                display_name=data["display"],
            )
            return MappingResult(
                original_term=term,
                ontology=self.ontology_name,
                references=[ref],
                best_match=ref,
                confidence=0.9,
                mapped=True,
            )
        
        return MappingResult(
            original_term=term,
            ontology=self.ontology_name,
            mapped=False,
        )
    
    async def get_details(self, code: str) -> Optional[OntologyReference]:
        """Obtiene detalles de código UMLS."""
        for key, data in self.UMLS_BASE.items():
            if data["cui"] == code:
                return OntologyReference(
                    reference_id=str(uuid.uuid4()),
                    ontology=self.ontology_name,
                    code=code,
                    display_name=data["display"],
                )
        return None


class MeSHMapper(BaseOntologyMapper):
    """Mapper para MeSH (Medical Subject Headings)."""
    
    MESH_BASE = {
        "heart disease": {
            "mesh_id": "D006331",
            "display": "Heart Diseases",
            "tree_numbers": ["C14.240"],
        },
        "diabetes mellitus": {
            "mesh_id": "D003920",
            "display": "Diabetes Mellitus",
            "tree_numbers": ["C19.246"],
        },
        "medical devices": {
            "mesh_id": "D008491",
            "display": "Medical Devices",
            "tree_numbers": ["E07.695"],
        },
        "biomedical engineering": {
            "mesh_id": "D017855",
            "display": "Biomedical Engineering",
            "tree_numbers": ["J01.097.120"],
        },
        "clinical engineering": {
            "mesh_id": "D017855",
            "display": "Biomedical Engineering",
            "tree_numbers": ["J01.097.120"],
        },
    }
    
    @property
    def ontology_name(self) -> str:
        return "MeSH"
    
    async def map_term(self, term: str) -> MappingResult:
        """Mapea término a MeSH."""
        term_lower = term.lower()
        
        if term_lower in self.MESH_BASE:
            data = self.MESH_BASE[term_lower]
            ref = OntologyReference(
                reference_id=str(uuid.uuid4()),
                ontology=self.ontology_name,
                code=data["mesh_id"],
                display_name=data["display"],
                hierarchy=data["tree_numbers"],
            )
            return MappingResult(
                original_term=term,
                ontology=self.ontology_name,
                references=[ref],
                best_match=ref,
                confidence=0.9,
                mapped=True,
            )
        
        return MappingResult(
            original_term=term,
            ontology=self.ontology_name,
            mapped=False,
        )
    
    async def get_details(self, code: str) -> Optional[OntologyReference]:
        """Obtiene detalles de código MeSH."""
        for key, data in self.MESH_BASE.items():
            if data["mesh_id"] == code:
                return OntologyReference(
                    reference_id=str(uuid.uuid4()),
                    ontology=self.ontology_name,
                    code=code,
                    display_name=data["display"],
                    hierarchy=data["tree_numbers"],
                )
        return None


class ICDMapper(BaseOntologyMapper):
    """Mapper para ICD-10."""
    
    ICD10_BASE = {
        "heart failure": {
            "code": "I50",
            "display": "Heart failure",
            "includes": ["cardiac failure", "myocardial failure"],
        },
        "diabetes": {
            "code": "E11",
            "display": "Type 2 diabetes mellitus",
            "includes": ["adult onset diabetes", "noninsulin dependent diabetes"],
        },
        "hypertension": {
            "code": "I10",
            "display": "Essential (primary) hypertension",
            "includes": ["high blood pressure", "HTN"],
        },
        "stroke": {
            "code": "I64",
            "display": "Stroke, not specified as hemorrhage or infarction",
            "includes": ["CVA", "cerebrovascular accident"],
        },
        "myocardial infarction": {
            "code": "I21",
            "display": "Acute myocardial infarction",
            "includes": ["heart attack", "MI"],
        },
    }
    
    @property
    def ontology_name(self) -> str:
        return "ICD-10"
    
    async def map_term(self, term: str) -> MappingResult:
        """Mapea término a ICD-10."""
        term_lower = term.lower()
        
        for key, data in self.ICD10_BASE.items():
            if term_lower == key or term_lower in key:
                ref = OntologyReference(
                    reference_id=str(uuid.uuid4()),
                    ontology=self.ontology_name,
                    code=data["code"],
                    display_name=data["display"],
                    synonyms=data["includes"],
                )
                return MappingResult(
                    original_term=term,
                    ontology=self.ontology_name,
                    references=[ref],
                    best_match=ref,
                    confidence=0.9,
                    mapped=True,
                )
            
            # Buscar en includes
            for inc in data.get("includes", []):
                if term_lower == inc.lower() or term_lower in inc.lower():
                    ref = OntologyReference(
                        reference_id=str(uuid.uuid4()),
                        ontology=self.ontology_name,
                        code=data["code"],
                        display_name=data["display"],
                        synonyms=data["includes"],
                    )
                    return MappingResult(
                        original_term=term,
                        ontology=self.ontology_name,
                        references=[ref],
                        best_match=ref,
                        confidence=0.8,
                        mapped=True,
                    )
        
        return MappingResult(
            original_term=term,
            ontology=self.ontology_name,
            mapped=False,
        )
    
    async def get_details(self, code: str) -> Optional[OntologyReference]:
        """Obtiene detalles de código ICD."""
        for key, data in self.ICD10_BASE.items():
            if data["code"] == code:
                return OntologyReference(
                    reference_id=str(uuid.uuid4()),
                    ontology=self.ontology_name,
                    code=code,
                    display_name=data["display"],
                    synonyms=data["includes"],
                )
        return None


class TerminologyMapperFactory:
    """Fábrica de mapeadores de terminología."""
    
    @staticmethod
    def create_snomed_mapper() -> SNOMEDMapper:
        """Crea mapper SNOMED."""
        return SNOMEDMapper()
    
    @staticmethod
    def create_umls_mapper() -> UMLSMapper:
        """Crea mapper UMLS."""
        return UMLSMapper()
    
    @staticmethod
    def create_mesh_mapper() -> MeSHMapper:
        """Crea mapper MeSH."""
        return MeSHMapper()
    
    @staticmethod
    def create_icd_mapper() -> ICDMapper:
        """Crea mapper ICD."""
        return ICDMapper()
    
    @staticmethod
    def create_all() -> dict[str, BaseOntologyMapper]:
        """Crea todos los mapeadores."""
        return {
            "SNOMED": SNOMEDMapper(),
            "UMLS": UMLSMapper(),
            "MeSH": MeSHMapper(),
            "ICD-10": ICDMapper(),
        }


__all__ = [
    "OntologyReference",
    "MappingResult",
    "BaseOntologyMapper",
    "SNOMEDMapper",
    "UMLSMapper",
    "MeSHMapper",
    "ICDMapper",
    "TerminologyMapperFactory",
]
