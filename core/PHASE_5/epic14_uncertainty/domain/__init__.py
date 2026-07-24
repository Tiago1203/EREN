"""
Domain objects para EPIC 14: Uncertainty Quantification Model
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class UncertaintyType(Enum):
    """Tipo de incertidumbre."""
    ALEATORY = "aleatory"  # Variabilidad inherente
    EPISTEMIC = "epistemic"  # Falta de conocimiento
    MODEL = "model"  # Limitaciones del modelo
    PARAMETRIC = "parametric"  # Incertidumbre en parámetros
    MEASUREMENT = "measurement"  # Errores de medición


class AudienceType(Enum):
    """Tipo de audiencia."""
    CLINICAL = "clinical"
    PATIENT = "patient"
    TECHNICAL = "technical"
    MANAGEMENT = "management"


class MitigationStrategy(Enum):
    """Estrategia de mitigación."""
    COLLECT_MORE_DATA = "collect_more_data"
    CONSULT_EXPERT = "consult_expert"
    USE_BAYESIAN = "use_bayesian"
    SENSITIVITY_ANALYSIS = "sensitivity_analysis"


@dataclass
class ProbabilityDistribution:
    """Distribución de probabilidad."""
    distribution_type: str
    parameters: dict
    mean: float
    std_dev: float
    
    def get_confidence_interval(self, level: float) -> tuple:
        """Obtiene intervalo de confianza."""
        # Simplified calculation
        z_score = 1.96 if level == 0.95 else 1.645
        return (self.mean - z_score * self.std_dev, self.mean + z_score * self.std_dev)


@dataclass
class UncertaintySource:
    """Fuente de incertidumbre."""
    source_id: str
    source_type: UncertaintyType
    description: str
    estimated_impact: float
    mitigatable: bool
    
    def get_mitigation_strategy(self) -> Optional[MitigationStrategy]:
        """Obtiene estrategia de mitigación."""
        if self.mitigatable:
            return MitigationStrategy.COLLECT_MORE_DATA
        return None


@dataclass
class Uncertainty:
    """Incertidumbre base."""
    uncertainty_id: str
    uncertainty_type: UncertaintyType
    value: float
    distribution: Optional[ProbabilityDistribution] = None
    sources: list[UncertaintySource] = field(default_factory=list)
    
    def get_confidence_interval(self, level: float = 0.95) -> tuple:
        """Obtiene intervalo de confianza."""
        if self.distribution:
            return self.distribution.get_confidence_interval(level)
        # Fallback: ±20% del valor
        margin = self.value * 0.2
        return (self.value - margin, self.value + margin)
    
    def get_variance(self) -> float:
        """Obtiene varianza."""
        if self.distribution:
            return self.distribution.std_dev ** 2
        return (self.value * 0.2) ** 2
    
    def get_std_deviation(self) -> float:
        """Obtiene desviación estándar."""
        if self.distribution:
            return self.distribution.std_dev
        return self.value * 0.2


@dataclass
class ConfidenceLevel:
    """Nivel de confianza."""
    level: float  # 0.0 - 1.0
    is_calibrated: bool
    calibration_error: Optional[float] = None
    based_on: list[str] = field(default_factory=list)
    
    def is_high_confidence(self) -> bool:
        """Verifica si es alta confianza."""
        return self.level >= 0.8
    
    def requires_qualification(self) -> bool:
        """Verifica si requiere cualificación."""
        return self.level < 0.7 or (self.calibration_error and self.calibration_error > 0.1)


@dataclass
class UncertaintyPropagation:
    """Propagación de incertidumbre."""
    propagation_id: str
    input_uncertainties: list[Uncertainty]
    output_uncertainty: Uncertainty
    method: str
    sensitivity_analysis: Optional[dict] = None
    
    def get_total_uncertainty(self) -> float:
        """Obtiene incertidumbre total."""
        return sum(u.value for u in self.input_uncertainties) / len(self.input_uncertainties)


@dataclass
class UncertaintyStatement:
    """Declaración de incertidumbre."""
    statement: str
    probability: Optional[float] = None
    confidence_interval: Optional[tuple] = None
    caveats: list[str] = field(default_factory=list)
    audience: AudienceType = AudienceType.CLINICAL
    
    def format_for_clinical(self) -> str:
        """Formatea para contexto clínico."""
        if self.probability:
            prob_str = f"{self.probability * 100:.0f}% probability"
        else:
            prob_str = ""
        
        if self.confidence_interval:
            ci_str = f" (95% CI: {self.confidence_interval[0]:.2f}-{self.confidence_interval[1]:.2f})"
        else:
            ci_str = ""
        
        caveats_str = ""
        if self.caveats:
            caveats_str = f" Caveats: {', '.join(self.caveats)}"
        
        return f"{prob_str}{ci_str}.{caveats_str}"


@dataclass
class ConfidenceInterval:
    """Intervalo de confianza."""
    lower: float
    upper: float
    level: float
    
    def contains(self, value: float) -> bool:
        """Verifica si el valor está en el intervalo."""
        return self.lower <= value <= self.upper


@dataclass
class UncertaintyConfig:
    """Configuración para UncertaintyAgent."""
    default_confidence_level: float = 0.95
    require_calibration: bool = True
    min_confidence_threshold: float = 0.5
