"""Prompt Optimizer - Optimizador de prompts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from core.PHASE_2.ai.prompt.models import PromptTemplate, RenderedPrompt


class PromptOptimizer:
    """
    Optimizador de prompts.
    
    Mejora prompts para mayor efectividad.
    """

    def __init__(
        self,
        aggressive: bool = False,
    ) -> None:
        self.aggressive = aggressive
        
        # Patrones de mejora
        self._redundant_patterns = [
            r'por favor\s+',
            r'podrías\s+',
            r'me puedes\s+',
            r'explica\s+',
            r'de manera\s+',
            r'en\s+detalle\s+',
        ]
        
        # Instrucciones de sistema problemáticas
        self._problematic_instructions = [
            "sé breve",
            "sé conciso",
            "no seas verbose",
            "evita explicaciones largas",
        ]

    def optimize_template(
        self,
        template: PromptTemplate,
    ) -> PromptTemplate:
        """
        Optimiza un template de prompt.
        
        Args:
            template: Template a optimizar
            
        Returns:
            Template optimizado
        """
        # Optimizar system template
        system = self._optimize_text(template.system_template)
        
        # Optimizar user template
        user = self._optimize_text(template.user_template)
        
        # Crear nuevo template con optimized
        optimized = PromptTemplate(
            id=f"{template.id}-optimized",
            name=f"{template.name} (Optimized)",
            version=template.version,
            description=f"Optimized version of {template.name}",
            strategy=template.strategy,
            system_template=system,
            user_template=user,
            variables=template.variables,
            examples=template.examples,
            metadata={**template.metadata, "optimized": True},
            max_tokens=template.max_tokens,
            temperature=template.temperature,
            model=template.model,
        )
        
        return optimized

    def optimize_rendered(
        self,
        rendered: RenderedPrompt,
    ) -> RenderedPrompt:
        """
        Optimiza un prompt ya renderizado.
        
        Args:
            rendered: Prompt renderizado
            
        Returns:
            Prompt optimizado
        """
        system = None
        if rendered.system_message:
            system = self._optimize_text(rendered.system_message)
        
        user = self._optimize_text(rendered.user_message)
        
        return RenderedPrompt(
            system_message=system,
            user_message=user,
            model=rendered.model,
            tokens_estimate=len(system or "") + len(user) // 4 if system else len(user) // 4,
            template_id=rendered.template_id,
            template_version=rendered.template_version,
        )

    def _optimize_text(self, text: str) -> str:
        """Aplica optimizaciones a un texto."""
        if not text:
            return text
        
        # 1. Remover espacios extra
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        if self.aggressive:
            # 2. Remover frases redundantes
            for pattern in self._redundant_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            # 3. Unir oraciones cortas relacionadas
            text = self._join_short_sentences(text)
            
            # 4. Remover instrucciones conflictivas
            for instruction in self._problematic_instructions:
                text = re.sub(instruction, '', text, flags=re.IGNORECASE)
        
        # 5. Normalizar puntuación
        text = self._normalize_punctuation(text)
        
        return text

    def _join_short_sentences(self, text: str) -> str:
        """Une oraciones cortas relacionadas."""
        # Unir oraciones muy cortas (< 30 chars) con la siguiente
        sentences = re.split(r'([.!?]\s+)', text)
        
        result = []
        buffer = ""
        
        for i, part in enumerate(sentences):
            if i % 2 == 0:  # Es texto, no puntuación
                buffer += part
                if len(buffer) > 30:
                    result.append(buffer)
                    buffer = ""
            else:  # Es puntuación
                if buffer:
                    buffer += part
                    if len(buffer) <= 30:
                        continue
                    result.append(buffer)
                    buffer = ""
                else:
                    result.append(part)
        
        if buffer:
            result.append(buffer)
        
        return "".join(result)

    def _normalize_punctuation(self, text: str) -> str:
        """Normaliza puntuación."""
        # Espacios antes de puntuación
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # Espacios después de puntuación
        text = re.sub(r'([.,;:!?])(?=[^\s])', r'\1 ', text)
        
        # Puntuación repetida
        text = re.sub(r'([.!?])\1+', r'\1', text)
        
        # Espacios múltiples
        text = re.sub(r'\s{2,}', ' ', text)
        
        return text.strip()


class PromptAnalyzer:
    """
    Analizador de prompts.
    
    Proporciona métricas y feedback sobre prompts.
    """

    def analyze(self, text: str) -> PromptAnalysis:
        """
        Analiza un prompt.
        
        Args:
            text: Texto del prompt
            
        Returns:
            Análisis del prompt
        """
        return PromptAnalysis(
            length=len(text),
            word_count=len(text.split()),
            sentence_count=self._count_sentences(text),
            token_estimate=len(text) // 4,
            clarity_score=self._calculate_clarity(text),
            complexity_score=self._calculate_complexity(text),
            has_clear_goal=self._has_clear_goal(text),
            has_constraints=self._has_constraints(text),
            suggestions=self._generate_suggestions(text),
        )

    def _count_sentences(self, text: str) -> int:
        """Cuenta oraciones."""
        return len(re.findall(r'[.!?]+', text))

    def _calculate_clarity(self, text: str) -> float:
        """Calcula score de claridad (0-1)."""
        score = 1.0
        
        # Penalizar si hay palabras muy largas
        long_words = sum(1 for word in text.split() if len(word) > 15)
        if long_words > 5:
            score -= 0.1 * (long_words - 5)
        
        # Penalizar oraciones muy largas
        sentences = re.split(r'[.!?]+', text)
        long_sentences = sum(1 for s in sentences if len(s.split()) > 30)
        if long_sentences > 2:
            score -= 0.1 * long_sentences
        
        # Bonificar si tiene estructura clara
        if text.startswith("[") or "##" in text:
            score += 0.1
        
        return max(0.0, min(1.0, score))

    def _calculate_complexity(self, text: str) -> float:
        """Calcula score de complejidad (0-1, 1 = muy complejo)."""
        # Basado en longitud y estructura
        word_count = len(text.split())
        sentence_count = max(1, self._count_sentences(text))
        
        avg_words_per_sentence = word_count / sentence_count
        
        # Normalizar: ~15 palabras = complejidad 0.5
        complexity = avg_words_per_sentence / 30
        
        return min(1.0, complexity)

    def _has_clear_goal(self, text: str) -> bool:
        """Verifica si tiene un objetivo claro."""
        goal_indicators = [
            "objetivo:", "meta:", "fin:",
            "debes", "necesito", "quiero",
            "tarea:", "incumbencia:",
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in goal_indicators)

    def _has_constraints(self, text: str) -> bool:
        """Verifica si tiene restricciones."""
        constraint_indicators = [
            "no", "evita", "no debes",
            "limita", "máximo", "mínimo",
            "restricción:", "constraint:",
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in constraint_indicators)

    def _generate_suggestions(self, text: str) -> list[str]:
        """Genera sugerencias de mejora."""
        suggestions = []
        
        if len(text.split()) < 20:
            suggestions.append("El prompt podría beneficiarse de más contexto")
        
        if not self._has_clear_goal(text):
            suggestions.append("Considera agregar un objetivo claro al inicio")
        
        if not self._has_constraints(text):
            suggestions.append("Podrías agregar restricciones para mejorar la respuesta")
        
        if self._count_sentences(text) < 3 and len(text) > 500:
            suggestions.append("El prompt tiene oraciones muy largas. Considera dividirlas")
        
        return suggestions


@dataclass
class PromptAnalysis:
    """Resultado del análisis de prompt."""
    length: int
    word_count: int
    sentence_count: int
    token_estimate: int
    clarity_score: float
    complexity_score: float
    has_clear_goal: bool
    has_constraints: bool
    suggestions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "length": self.length,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "token_estimate": self.token_estimate,
            "clarity_score": self.clarity_score,
            "complexity_score": self.complexity_score,
            "has_clear_goal": self.has_clear_goal,
            "has_constraints": self.has_constraints,
            "suggestions": self.suggestions,
        }


from dataclasses import dataclass
