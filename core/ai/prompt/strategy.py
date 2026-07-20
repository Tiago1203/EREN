"""Prompt Strategy - Estrategias de prompt."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.ai.prompt.models import (
    PromptExample,
    PromptStrategyType,
    PromptTemplate,
    RenderedPrompt,
)
from core.ai.prompt.renderer import PromptRenderer


class PromptStrategy(ABC):
    """Estrategia base de prompt."""
    
    @abstractmethod
    def apply(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample] | None = None,
    ) -> RenderedPrompt:
        """Aplica la estrategia al template."""
        ...
    
    @property
    @abstractmethod
    def strategy_type(self) -> PromptStrategyType:
        """Tipo de estrategia."""
        ...


class DirectStrategy(PromptStrategy):
    """Estrategia directa - pregunta simple."""
    
    @property
    def strategy_type(self) -> PromptStrategyType:
        return PromptStrategyType.DIRECT
    
    def apply(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample] | None = None,
    ) -> RenderedPrompt:
        renderer = PromptRenderer()
        return renderer.render(template, variables, self.strategy_type, examples)


class ChainOfThoughtStrategy(PromptStrategy):
    """
    Estrategia Chain of Thought.
    
    Agrega instrucciones para razonamiento paso a paso.
    """
    
    def __init__(
        self,
        include_examples: bool = True,
        show_reasoning: bool = True,
    ) -> None:
        self.include_examples = include_examples
        self.show_reasoning = show_reasoning
    
    @property
    def strategy_type(self) -> PromptStrategyType:
        return PromptStrategyType.CHAIN_OF_THOUGHT
    
    def apply(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample] | None = None,
    ) -> RenderedPrompt:
        renderer = PromptRenderer()
        return renderer.render(template, variables, self.strategy_type, examples)


class FewShotStrategy(PromptStrategy):
    """
    Estrategia Few-Shot Learning.
    
    Incluye ejemplos en el prompt.
    """
    
    def __init__(
        self,
        max_examples: int = 5,
        include_explanations: bool = True,
    ) -> None:
        self.max_examples = max_examples
        self.include_explanations = include_explanations
    
    @property
    def strategy_type(self) -> PromptStrategyType:
        return PromptStrategyType.FEW_SHOT
    
    def apply(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample] | None = None,
    ) -> RenderedPrompt:
        # Limitar ejemplos
        limited_examples = None
        if examples:
            limited_examples = examples[:self.max_examples]
        
        renderer = PromptRenderer()
        return renderer.render(template, variables, self.strategy_type, limited_examples)


class TreeOfThoughtStrategy(PromptStrategy):
    """
    Estrategia Tree of Thought.
    
    Explora múltiples caminos de razonamiento.
    """
    
    def __init__(
        self,
        num_branches: int = 3,
        evaluation_enabled: bool = True,
    ) -> None:
        self.num_branches = num_branches
        self.evaluation_enabled = evaluation_enabled
    
    @property
    def strategy_type(self) -> PromptStrategyType:
        return PromptStrategyType.TREE_OF_THOUGHT
    
    def apply(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample] | None = None,
    ) -> RenderedPrompt:
        renderer = PromptRenderer()
        return renderer.render(template, variables, self.strategy_type, examples)


class ReActStrategy(PromptStrategy):
    """
    Estrategia ReAct (Reason + Act).
    
    Combina razonamiento con acciones.
    """
    
    def __init__(
        self,
        max_steps: int = 5,
        include_observations: bool = True,
    ) -> None:
        self.max_steps = max_steps
        self.include_observations = include_observations
    
    @property
    def strategy_type(self) -> PromptStrategyType:
        return PromptStrategyType.REACT
    
    def apply(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample] | None = None,
    ) -> RenderedPrompt:
        renderer = PromptRenderer()
        return renderer.render(template, variables, self.strategy_type, examples)


class SelfAskStrategy(PromptStrategy):
    """
    Estrategia Self-Ask.
    
    El modelo hace preguntas intermedias.
    """
    
    def __init__(
        self,
        follow_up_enabled: bool = True,
    ) -> None:
        self.follow_up_enabled = follow_up_enabled
    
    @property
    def strategy_type(self) -> PromptStrategyType:
        return PromptStrategyType.SELF_ASK
    
    def apply(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample] | None = None,
    ) -> RenderedPrompt:
        # Agregar instrucción de self-ask
        variables["_self_ask_instruction"] = """
Antes de responder, hazte preguntas intermedias como:
- ¿Qué información necesito?
- ¿Hay algo que deba verificar?
- ¿Qué posibles respuestas hay?

Responde cada pregunta antes de dar la respuesta final.
"""
        
        renderer = PromptRenderer()
        return renderer.render(template, variables, PromptStrategyType.DIRECT, examples)


class StrategyFactory:
    """Fábrica de estrategias."""
    
    def __init__(self) -> None:
        self._strategies: dict[PromptStrategyType, type[PromptStrategy]] = {
            PromptStrategyType.DIRECT: DirectStrategy,
            PromptStrategyType.CHAIN_OF_THOUGHT: ChainOfThoughtStrategy,
            PromptStrategyType.FEW_SHOT: FewShotStrategy,
            PromptStrategyType.ZERO_SHOT: DirectStrategy,  # Zero-shot usa direct
            PromptStrategyType.TREE_OF_THOUGHT: TreeOfThoughtStrategy,
            PromptStrategyType.REACT: ReActStrategy,
            PromptStrategyType.SELF_ASK: SelfAskStrategy,
            PromptStrategyType.REFLEXION: DirectStrategy,  # Placeholder
        }
        self._instances: dict[PromptStrategyType, PromptStrategy] = {}
    
    def get_strategy(
        self,
        strategy_type: PromptStrategyType,
        **kwargs: Any,
    ) -> PromptStrategy:
        """Obtiene una instancia de estrategia."""
        if strategy_type not in self._instances:
            strategy_class = self._strategies.get(strategy_type, DirectStrategy)
            self._instances[strategy_type] = strategy_class(**kwargs)
        
        return self._instances[strategy_type]
    
    def register_strategy(
        self,
        strategy_type: PromptStrategyType,
        strategy_class: type[PromptStrategy],
    ) -> None:
        """Registra una nueva estrategia."""
        self._strategies[strategy_type] = strategy_class
        if strategy_type in self._instances:
            del self._instances[strategy_type]
    
    def clear_cache(self) -> None:
        """Limpia el caché de instancias."""
        self._instances.clear()
