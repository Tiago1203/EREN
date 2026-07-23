"""
Inference Engine Module

Complete implementation for forward/backward chaining,
abductive reasoning, and Bayesian inference.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol
from collections import deque


class InferenceType(Enum):
    """Types of inference."""
    FORWARD_CHAINING = "forward_chaining"
    BACKWARD_CHAINING = "backward_chaining"
    ABDUCTIVE = "abductive"
    BAYESIAN = "bayesian"


@dataclass(frozen=True)
class Fact:
    """A fact or assertion."""
    fact_id: str
    content: str
    confidence: float = 1.0
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class InferenceRule:
    """A rule for inference."""
    rule_id: str
    name: str
    antecedents: list[str]  # Fact IDs or conditions
    consequents: list[str]  # Fact IDs that can be inferred
    confidence: float = 1.0
    source: str = "unknown"
    conditions: list[str] = field(default_factory=list)  # Additional conditions


@dataclass(frozen=True)
class InferenceStep:
    """A step in an inference chain."""
    step_number: int
    rule_id: str
    facts_used: list[str]
    facts_derived: list[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class InferenceResult:
    """Result of an inference operation."""
    inferred_facts: list[Fact]
    inference_chain: list[InferenceStep]
    applied_rules: list[str]
    iterations: int
    confidence: float
    success: bool


@dataclass
class ProofTree:
    """Proof tree for backward chaining."""
    goal: str
    sub_goals: list[str]
    supporting_rules: list[str]
    proven: bool
    branches: list["ProofTree"] = field(default_factory=list)


class ForwardChaining:
    """
    Forward chaining inference engine.
    Applies rules from known facts to derive new facts.
    """
    
    def __init__(self):
        self._rules: list[InferenceRule] = []
    
    async def add_rule(self, rule: InferenceRule) -> None:
        """Add a rule to the engine."""
        self._rules.append(rule)
    
    async def chain(
        self,
        facts: list[Fact],
        max_iterations: int = 100,
    ) -> InferenceResult:
        """Execute forward chaining inference."""
        known_fact_ids = {f.fact_id for f in facts}
        known_contents = {f.content.lower() for f in facts}
        inferred_facts: list[Fact] = list(facts)
        applied_rules: set[str] = set()
        chain: list[InferenceStep] = []
        
        for iteration in range(max_iterations):
            new_facts_found = False
            
            for rule in self._rules:
                if rule.rule_id in applied_rules:
                    continue
                
                # Check if antecedents are satisfied
                if self._can_apply_rule(rule, known_fact_ids, known_contents):
                    # Apply rule
                    for consequent in rule.consequents:
                        new_fact = Fact(
                            fact_id=f"inferred_{consequent}_{iteration}",
                            content=consequent,
                            confidence=rule.confidence,
                            source=f"rule:{rule.rule_id}",
                        )
                        
                        if (new_fact.content.lower() not in known_contents and
                            new_fact.fact_id not in known_fact_ids):
                            inferred_facts.append(new_fact)
                            known_fact_ids.add(new_fact.fact_id)
                            known_contents.add(new_fact.content.lower())
                            new_facts_found = True
                            
                            chain.append(InferenceStep(
                                step_number=len(chain),
                                rule_id=rule.rule_id,
                                facts_used=list(rule.antecedents),
                                facts_derived=[consequent],
                                confidence=rule.confidence,
                            ))
                    
                    applied_rules.add(rule.rule_id)
            
            if not new_facts_found:
                break
        
        # Calculate overall confidence
        overall_confidence = 1.0
        if chain:
            for step in chain:
                overall_confidence *= step.confidence
        
        return InferenceResult(
            inferred_facts=inferred_facts,
            inference_chain=chain,
            applied_rules=list(applied_rules),
            iterations=iteration + 1,
            confidence=overall_confidence,
            success=True,
        )
    
    def _can_apply_rule(
        self,
        rule: InferenceRule,
        known_fact_ids: set[str],
        known_contents: set[str],
    ) -> bool:
        """Check if rule can be applied."""
        for antecedent in rule.antecedents:
            # Check by ID
            if antecedent in known_fact_ids:
                continue
            # Check by content (case insensitive)
            if antecedent.lower() in known_contents:
                continue
            return False
        return True


class BackwardChaining:
    """
    Backward chaining inference engine.
    Starts from goal and works backwards to find supporting facts.
    """
    
    def __init__(self):
        self._rules: list[InferenceRule] = []
    
    async def add_rule(self, rule: InferenceRule) -> None:
        """Add a rule to the engine."""
        self._rules.append(rule)
    
    async def chain(
        self,
        goal: str,
        known_facts: list[Fact],
    ) -> tuple[bool, ProofTree]:
        """Execute backward chaining to prove goal."""
        known_ids = {f.fact_id for f in known_facts}
        known_contents = {f.content.lower() for f in known_facts}
        
        # Check if goal is already known
        if goal.lower() in known_contents or goal in known_ids:
            return True, ProofTree(
                goal=goal,
                sub_goals=[],
                supporting_rules=[],
                proven=True,
            )
        
        # Find rules that can derive goal
        supporting_rules = [
            r for r in self._rules
            if goal in r.consequents
        ]
        
        if not supporting_rules:
            return False, ProofTree(
                goal=goal,
                sub_goals=[],
                supporting_rules=[],
                proven=False,
            )
        
        # Try each supporting rule
        for rule in supporting_rules:
            proof = await self._prove_with_rule(
                rule, known_ids, known_contents
            )
            if proof.proven:
                return True, proof
        
        return False, ProofTree(
            goal=goal,
            sub_goals=[],
            supporting_rules=[r.rule_id for r in supporting_rules],
            proven=False,
        )
    
    async def _prove_with_rule(
        self,
        rule: InferenceRule,
        known_ids: set[str],
        known_contents: set[str],
    ) -> ProofTree:
        """Try to prove using a specific rule."""
        sub_goals = []
        all_proven = True
        
        for antecedent in rule.antecedents:
            if antecedent in known_ids or antecedent.lower() in known_contents:
                sub_goals.append(f"{antecedent} (known)")
            else:
                # Recursively prove antecedent
                proven, _ = await self.chain(antecedent, [])
                if proven:
                    sub_goals.append(f"{antecedent} (proven)")
                else:
                    sub_goals.append(f"{antecedent} (failed)")
                    all_proven = False
        
        return ProofTree(
            goal=rule.consequents[0] if rule.consequents else "",
            sub_goals=sub_goals,
            supporting_rules=[rule.rule_id],
            proven=all_proven,
        )


class AbductiveReasoning:
    """
    Abductive reasoning engine.
    Generates best explanations for observations.
    """
    
    def __init__(self):
        self._rules: list[InferenceRule] = []
        self._explanations: list[dict] = []
    
    async def add_explanation_pattern(
        self,
        observation: str,
        possible_causes: list[str],
        plausibility: float,
    ) -> None:
        """Add an explanation pattern."""
        self._explanations.append({
            "observation": observation,
            "causes": possible_causes,
            "plausibility": plausibility,
        })
    
    async def explain(
        self,
        observation: str,
        max_explanations: int = 5,
    ) -> list[dict]:
        """Generate explanations for an observation."""
        explanations = []
        
        for pattern in self._explanations:
            if observation.lower() in pattern["observation"].lower():
                for cause in pattern["causes"]:
                    explanations.append({
                        "cause": cause,
                        "observation": observation,
                        "plausibility": pattern["plausibility"],
                        "confidence": pattern["plausibility"],
                    })
        
        # Sort by plausibility
        explanations.sort(key=lambda x: x["plausibility"], reverse=True)
        return explanations[:max_explanations]
    
    async def find_best_explanation(
        self,
        observations: list[str],
    ) -> dict | None:
        """Find the best explanation for multiple observations."""
        explanations = []
        
        for obs in observations:
            obs_explanations = await self.explain(obs)
            for exp in obs_explanations:
                explanations.append(exp)
        
        if not explanations:
            return None
        
        # Combine explanations that share common causes
        cause_scores: dict[str, float] = {}
        for exp in explanations:
            cause = exp["cause"]
            if cause not in cause_scores:
                cause_scores[cause] = 0
            cause_scores[cause] += exp["plausibility"]
        
        # Find cause with highest score
        if cause_scores:
            best_cause = max(cause_scores.items(), key=lambda x: x[1])
            return {
                "cause": best_cause[0],
                "confidence": best_cause[1] / len(observations),
                "observations_explained": len(observations),
            }
        
        return None


class BayesianInference:
    """
    Bayesian inference engine.
    Updates probabilities based on evidence.
    """
    
    async def update_probability(
        self,
        prior: float,
        likelihood: float,
        evidence_prior: float | None = None,
    ) -> float:
        """
        Update probability using Bayes' theorem.
        P(H|E) = P(E|H) * P(H) / P(E)
        """
        if evidence_prior is None:
            # Approximate P(E) = P(E|H) * P(H) + P(E|~H) * P(~H)
            evidence_prior = (likelihood * prior) + ((1 - likelihood) * (1 - prior))
        
        if evidence_prior == 0:
            return prior
        
        posterior = (likelihood * prior) / evidence_prior
        return min(max(posterior, 0.0), 1.0)
    
    async def calculate_likelihood_ratio(
        self,
        sensitivity: float,
        specificity: float,
    ) -> float:
        """Calculate likelihood ratio."""
        if (1 - specificity) == 0:
            return float('inf')
        return sensitivity / (1 - specificity)
    
    async def update_from_evidence(
        self,
        prior: float,
        evidence_list: list[dict],  # [{likelihood: float, weight: float}]
    ) -> float:
        """Update probability from multiple evidence."""
        posterior = prior
        
        for evidence in evidence_list:
            likelihood = evidence.get("likelihood", 0.5)
            weight = evidence.get("weight", 1.0)
            
            # Weighted likelihood
            weighted_likelihood = (likelihood * weight + 0.5 * (1 - weight))
            posterior = await self.update_probability(posterior, weighted_likelihood)
        
        return posterior


class InferenceEngine:
    """
    Complete inference engine with multiple reasoning strategies.
    """
    
    def __init__(self):
        self.forward = ForwardChaining()
        self.backward = BackwardChaining()
        self.abductive = AbductiveReasoning()
        self.bayesian = BayesianInference()
        self._rules: list[InferenceRule] = []
    
    async def add_rule(self, rule: InferenceRule) -> None:
        """Add a rule to all inference strategies."""
        self._rules.append(rule)
        await self.forward.add_rule(rule)
        await self.backward.add_rule(rule)
    
    async def reason(
        self,
        inference_type: InferenceType,
        **kwargs,
    ) -> InferenceResult:
        """Execute reasoning with specified strategy."""
        if inference_type == InferenceType.FORWARD_CHAINING:
            facts = kwargs.get("facts", [])
            return await self.forward.chain(facts)
        
        elif inference_type == InferenceType.BACKWARD_CHAINING:
            goal = kwargs.get("goal", "")
            facts = kwargs.get("facts", [])
            proven, tree = await self.backward.chain(goal, facts)
            return InferenceResult(
                inferred_facts=[],
                inference_chain=[],
                applied_rules=tree.supporting_rules,
                iterations=1,
                confidence=1.0 if proven else 0.0,
                success=proven,
            )
        
        elif inference_type == InferenceType.ABDUCTIVE:
            observation = kwargs.get("observation", "")
            explanations = await self.abductive.explain(observation)
            return InferenceResult(
                inferred_facts=[],
                inference_chain=[],
                applied_rules=[],
                iterations=1,
                confidence=explanations[0]["plausibility"] if explanations else 0.0,
                success=len(explanations) > 0,
            )
        
        elif inference_type == InferenceType.BAYESIAN:
            prior = kwargs.get("prior", 0.5)
            evidence = kwargs.get("evidence", [])
            posterior = await self.bayesian.update_from_evidence(prior, evidence)
            return InferenceResult(
                inferred_facts=[Fact(
                    fact_id="bayesian_posterior",
                    content=f"Updated probability: {posterior}",
                    confidence=posterior,
                )],
                inference_chain=[],
                applied_rules=["bayesian_update"],
                iterations=1,
                confidence=posterior,
                success=True,
            )
        
        return InferenceResult(
            inferred_facts=[],
            inference_chain=[],
            applied_rules=[],
            iterations=0,
            confidence=0.0,
            success=False,
        )


__all__ = [
    "InferenceType",
    "Fact",
    "InferenceRule",
    "InferenceStep",
    "InferenceResult",
    "ProofTree",
    "ForwardChaining",
    "BackwardChaining",
    "AbductiveReasoning",
    "BayesianInference",
    "InferenceEngine",
]
