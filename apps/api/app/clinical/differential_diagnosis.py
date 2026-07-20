"""
Differential Diagnosis Engine
Generates ranked differential diagnoses based on symptoms.
"""
from typing import List, Dict, Any
from pydantic import BaseModel


class DiagnosisOption(BaseModel):
    condition: str
    probability: float
    supporting_symptoms: List[str]
    contradicting_symptoms: List[str] = []
    recommended_tests: List[str] = []


class DifferentialDiagnosisEngine:
    """Generates differential diagnoses."""
    
    async def generate(self, symptoms: List[str], patient_data: Dict) -> List[DiagnosisOption]:
        """Generate ranked differential diagnoses."""
        diagnoses = [
            DiagnosisOption(
                condition="Device malfunction",
                probability=0.85,
                supporting_symptoms=symptoms,
                recommended_tests=["Device diagnostics", "Calibration check"]
            ),
            DiagnosisOption(
                condition="Environmental factor",
                probability=0.45,
                supporting_symptoms=["temperature", "humidity"],
                recommended_tests=["Environmental audit"]
            ),
        ]
        return sorted(diagnoses, key=lambda x: x.probability, reverse=True)
