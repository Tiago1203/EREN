"""
Reasoning Pipeline Module

Complete implementation for the reasoning pipeline that orchestrates
all reasoning components.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from core.PHASE_3.intelligence.reasoning.context import ReasoningContext
from core.PHASE_3.intelligence.reasoning.hypothesis import HypothesisEngine, HypothesisSet, Symptom, Evidence
from core.PHASE_3.intelligence.reasoning.inference import InferenceEngine, InferenceType
from core.PHASE_3.intelligence.reasoning.diagnostic import DiagnosticEngine, DifferentialDiagnosis
from core.PHASE_3.intelligence.reasoning.chains import ReasoningChain, ChainBuilder, ChainValidator, ChainType
from core.PHASE_3.intelligence.reasoning.causal import CausalGraph, CausalReasoner


@dataclass
class ReasoningInput:
    """Input to the reasoning pipeline."""
    query: str
    symptoms: list[Symptom]
    context: ReasoningContext
    equipment_type: Optional[str] = None


@dataclass
class ReasoningOutput:
    """Output from the reasoning pipeline."""
    hypothesis_set: HypothesisSet
    diagnosis: DifferentialDiagnosis
    reasoning_chains: list[ReasoningChain]
    confidence: float
    recommendations: list[str]
    timestamp: datetime = field(default_factory=datetime.now)


class ReasoningPipeline:
    """
    Main reasoning pipeline that orchestrates all reasoning components.
    """
    
    def __init__(self):
        self.hypothesis_engine = HypothesisEngine()
        self.inference_engine = InferenceEngine()
        self.diagnostic_engine = DiagnosticEngine()
        self.chain_builder = ChainBuilder()
        self.chain_validator = ChainValidator()
        self.causal_reasoner = CausalReasoner()
    
    async def reason(self, input_data: ReasoningInput) -> ReasoningOutput:
        """Execute the complete reasoning pipeline."""
        
        # Stage 1: Hypothesis Generation
        hypothesis_set = await self.hypothesis_engine.generate_hypotheses(
            symptoms=input_data.symptoms,
            equipment_type=input_data.equipment_type,
        )
        
        # Stage 2: Inference
        evidence_list = [
            {"likelihood": h.probability, "weight": h.confidence}
            for h in hypothesis_set.hypotheses
        ]
        await self.inference_engine.reason(
            InferenceType.BAYESIAN,
            prior=0.5,
            evidence=evidence_list,
        )
        
        # Stage 3: Diagnosis
        symptom_names = [s.name for s in input_data.symptoms]
        diagnosis = await self.diagnostic_engine.diagnose(
            symptoms=symptom_names,
            evidence=[{"supporting": True, "weight": 0.7}],
        )
        
        # Stage 4: Build Reasoning Chains
        reasoning_chains = await self._build_chains(
            hypothesis_set, diagnosis, input_data.query
        )
        
        # Stage 5: Validate Chains
        validated_chains = []
        for chain in reasoning_chains:
            is_valid, errors = await self.chain_validator.validate(chain)
            if is_valid:
                validated_chains.append(chain)
        
        # Calculate overall confidence
        confidence = self._calculate_overall_confidence(hypothesis_set, diagnosis)
        
        # Generate recommendations
        recommendations = self._extract_recommendations(diagnosis, hypothesis_set)
        
        return ReasoningOutput(
            hypothesis_set=hypothesis_set,
            diagnosis=diagnosis,
            reasoning_chains=validated_chains,
            confidence=confidence,
            recommendations=recommendations,
        )
    
    async def _build_chains(
        self,
        hypothesis_set: HypothesisSet,
        diagnosis: DifferentialDiagnosis,
        query: str,
    ) -> list[ReasoningChain]:
        """Build reasoning chains from hypotheses and diagnosis."""
        chains = []
        
        # Build chain from top hypothesis
        if hypothesis_set.primary_hypothesis:
            chain = await self.chain_builder.build_from_premises(
                premises=[query, hypothesis_set.primary_hypothesis.description],
                chain_type=ChainType.DEDUCTIVE,
            )
            
            # Add inference step
            chain = await self.chain_builder.add_inference_step(
                chain=chain,
                inference=f"Based on evidence, {hypothesis_set.primary_hypothesis.name} is most likely",
                rule="evidence_based_inference",
                supporting_steps=[0, 1],
            )
            
            # Add conclusion
            if diagnosis.most_likely:
                chain = await self.chain_builder.add_conclusion(
                    chain=chain,
                    conclusion=diagnosis.most_likely.condition,
                    supporting_steps=[0, 1, 2],
                )
            
            chains.append(chain)
        
        return chains
    
    def _calculate_overall_confidence(
        self,
        hypothesis_set: HypothesisSet,
        diagnosis: DifferentialDiagnosis,
    ) -> float:
        """Calculate overall confidence."""
        hypothesis_confidence = sum(
            h.confidence * h.probability
            for h in hypothesis_set.hypotheses
        ) / max(len(hypothesis_set.hypotheses), 1)
        
        diagnosis_confidence = (
            diagnosis.most_likely.confidence
            if diagnosis.most_likely
            else 0.5
        )
        
        return (hypothesis_confidence + diagnosis_confidence) / 2
    
    def _extract_recommendations(
        self,
        diagnosis: DifferentialDiagnosis,
        hypothesis_set: HypothesisSet,
    ) -> list[str]:
        """Extract recommendations from diagnosis and hypotheses."""
        recommendations = []
        
        for d in diagnosis.diagnoses[:3]:
            for rec in d.recommendations:
                recommendations.append(rec.action)
        
        return list(set(recommendations))[:5]


class ReasoningEngine:
    """
    Main reasoning engine that provides the external interface.
    """
    
    def __init__(self):
        self.pipeline = ReasoningPipeline()
    
    async def reason(
        self,
        query: str,
        symptoms: list[str],
        context: ReasoningContext,
        equipment_type: Optional[str] = None,
    ) -> ReasoningOutput:
        """Reason about a clinical problem."""
        # Convert symptoms strings to Symptom objects
        symptom_objects = [
            Symptom(
                symptom_id=f"s_{i}",
                name=s,
                description=s,
            )
            for i, s in enumerate(symptoms)
        ]
        
        input_data = ReasoningInput(
            query=query,
            symptoms=symptom_objects,
            context=context,
            equipment_type=equipment_type,
        )
        
        return await self.pipeline.reason(input_data)


__all__ = [
    "ReasoningInput",
    "ReasoningOutput",
    "ReasoningPipeline",
    "ReasoningEngine",
]
