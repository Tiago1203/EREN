"""Prompt Renderer - Renderizador de prompts."""

from __future__ import annotations

import time
import re
from typing import Any

from core.PHASE_2.ai.prompt.models import (
    PromptExample,
    PromptModel,
    PromptStrategyType,
    PromptTemplate,
    PromptVariable,
    PromptRole,
    RenderedPrompt,
)


class PromptRenderer:
    """
    Renderizador de prompts.
    
    Convierte templates en prompts renderizados
    listos para enviar al LLM.
    """

    def __init__(
        self,
        enable_syntax_highlighting: bool = False,
        default_model: PromptModel | None = None,
    ) -> None:
        self.enable_syntax_highlighting = enable_syntax_highlighting
        self.default_model = default_model
        self._variable_pattern = re.compile(r'\{\{(\w+)\}\}')

    def render(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        strategy: PromptStrategyType | None = None,
        examples: list[PromptExample] | None = None,
    ) -> RenderedPrompt:
        """
        Renderiza un template con variables.
        
        Args:
            template: Template de prompt
            variables: Valores de variables
            strategy: Estrategia a usar (None = del template)
            examples: Ejemplos override
            
        Returns:
            Prompt renderizado
        """
        start_time = time.time()
        
        # Validar variables
        valid, errors = template.validate_variables(variables)
        if not valid:
            raise ValueError(f"Validación de variables falló: {errors}")
        
        # Usar estrategia del template si no se especifica
        strategy = strategy or template.strategy
        
        # Usar ejemplos del template si no se especifican
        examples = examples or template.examples
        
        # Renderizar según estrategia
        if strategy == PromptStrategyType.CHAIN_OF_THOUGHT:
            return self._render_cot(template, variables, examples)
        elif strategy == PromptStrategyType.FEW_SHOT:
            return self._render_few_shot(template, variables, examples)
        elif strategy == PromptStrategyType.TREE_OF_THOUGHT:
            return self._render_tot(template, variables, examples)
        elif strategy == PromptStrategyType.REACT:
            return self._render_react(template, variables, examples)
        else:
            return self._render_direct(template, variables)

    def _render_direct(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
    ) -> RenderedPrompt:
        """Renderiza prompt directo."""
        system = self._interpolate(template.system_template, variables)
        user = self._interpolate(template.user_template, variables)
        
        return RenderedPrompt(
            system_message=system if system else None,
            user_message=user,
            model=template.model or self.default_model,
            tokens_estimate=self._estimate_tokens(system, user),
            template_id=template.id,
            template_version=template.version,
        )

    def _render_cot(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample],
    ) -> RenderedPrompt:
        """Renderiza prompt con Chain of Thought."""
        # Agregar instruction de COT
        cot_instruction = "\n\nAntes de dar la respuesta final, piensa paso a paso."
        
        system = self._interpolate(template.system_template, variables)
        user = self._interpolate(template.user_template, variables) + cot_instruction
        
        # Agregar ejemplos si hay
        if examples:
            examples_text = self._format_examples(examples, include_thinking=True)
            user = f"{examples_text}\n\nAhora resuelve el siguiente problema:\n\n{user}"
        
        return RenderedPrompt(
            system_message=system if system else None,
            user_message=user,
            model=template.model or self.default_model,
            tokens_estimate=self._estimate_tokens(system, user),
            template_id=template.id,
            template_version=template.version,
        )

    def _render_few_shot(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample],
    ) -> RenderedPrompt:
        """Renderiza prompt con Few-Shot Learning."""
        system = self._interpolate(template.system_template, variables)
        user = self._interpolate(template.user_template, variables)
        
        # Agregar ejemplos
        if examples:
            examples_text = self._format_examples(examples)
            user = f"{examples_text}\n\nAhora resuelve:\n\n{user}"
        
        return RenderedPrompt(
            system_message=system if system else None,
            user_message=user,
            model=template.model or self.default_model,
            tokens_estimate=self._estimate_tokens(system, user),
            template_id=template.id,
            template_version=template.version,
        )

    def _render_tot(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample],
    ) -> RenderedPrompt:
        """Renderiza prompt con Tree of Thought."""
        tot_instruction = """
\n\nPara problemas complejos, explora múltiples caminos de razonamiento:
1. Considera diferentes perspectivas
2. Evalúa los pros y contras de cada opción
3. Selecciona la mejor aproximación
"""
        
        system = self._interpolate(template.system_template, variables)
        user = self._interpolate(template.user_template, variables) + tot_instruction
        
        return RenderedPrompt(
            system_message=system if system else None,
            user_message=user,
            model=template.model or self.default_model,
            tokens_estimate=self._estimate_tokens(system, user),
            template_id=template.id,
            template_version=template.version,
        )

    def _render_react(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        examples: list[PromptExample],
    ) -> RenderedPrompt:
        """Renderiza prompt con ReAct (Reason + Act)."""
        react_instruction = """
\n\nUsa el siguiente formato:
1. Thought: [tu razonamiento sobre qué hacer]
2. Action: [la acción a tomar, si es necesaria]
3. Observation: [el resultado de la acción]
4. ... (repite según sea necesario)
5. Final Answer: [tu respuesta final]
"""
        
        system = self._interpolate(template.system_template, variables)
        user = self._interpolate(template.user_template, variables) + react_instruction
        
        return RenderedPrompt(
            system_message=system if system else None,
            user_message=user,
            model=template.model or self.default_model,
            tokens_estimate=self._estimate_tokens(system, user),
            template_id=template.id,
            template_version=template.version,
        )

    def _interpolate(
        self,
        template: str,
        variables: dict[str, Any],
    ) -> str:
        """
        Interpola variables en un template.
        
        Soporta sintaxis {{variable}} y {{variable|default}}.
        """
        def replace(match: re.Match) -> str:
            var_expr = match.group(1)
            
            # Parsear expresión con default
            if '|' in var_expr:
                var_name, default_value = var_expr.split('|', 1)
                var_name = var_name.strip()
                default_value = default_value.strip()
            else:
                var_name = var_expr.strip()
                default_value = None
            
            # Obtener valor
            if var_name in variables:
                value = variables[var_name]
                if value is None:
                    return default_value or ""
                return str(value)
            else:
                return default_value or ""
        
        return self._variable_pattern.sub(replace, template)

    def _format_examples(
        self,
        examples: list[PromptExample],
        include_thinking: bool = False,
    ) -> str:
        """Formatea ejemplos para few-shot."""
        parts = ["Ejemplos:\n"]
        
        for i, example in enumerate(examples, 1):
            parts.append(f"\n--- Ejemplo {i} ---")
            parts.append(f"\nInput: {example.input}")
            
            if include_thinking:
                parts.append("\nThought: Déjame pensar paso a paso...")
            
            parts.append(f"\nOutput: {example.output}")
            
            if example.explanation:
                parts.append(f"\nExplicación: {example.explanation}")
        
        return "\n".join(parts)

    def _estimate_tokens(self, system: str | None, user: str) -> int:
        """Estimación de tokens (~4 caracteres por token)."""
        total_chars = len(user)
        if system:
            total_chars += len(system)
        return total_chars // 4

    def render_to_string(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        strategy: PromptStrategyType | None = None,
    ) -> str:
        """Renderiza y devuelve como string único."""
        rendered = self.render(template, variables, strategy)
        
        parts = []
        if rendered.system_message:
            parts.append(f"[SYSTEM]\n{rendered.system_message}")
        parts.append(f"[USER]\n{rendered.user_message}")
        
        return "\n\n".join(parts)


class ModelPromptAdapter:
    """
    Adaptador de prompts para diferentes modelos.
    
    Ajusta el formato de prompts según el modelo destino.
    """

    def __init__(self) -> None:
        self._adapters: dict[PromptModel, ModelAdapter] = {
            PromptModel.GPT_4: OpenAIAdapter(),
            PromptModel.GPT_4_TURBO: OpenAIAdapter(),
            PromptModel.GPT_35_TURBO: OpenAIAdapter(),
            PromptModel.CLAUDE_3_OPUS: AnthropicAdapter(),
            PromptModel.CLAUDE_3_SONNET: AnthropicAdapter(),
            PromptModel.CLAUDE_3_HAIKU: AnthropicAdapter(),
            PromptModel.CLAUDE_2_1: AnthropicAdapter(),
            PromptModel.CLAUDE_2: AnthropicAdapter(),
            PromptModel.GEMINI_PRO: GeminiAdapter(),
            PromptModel.GEMINI_ULTRA: GeminiAdapter(),
        }
        self._default = OpenAIAdapter()

    def adapt(
        self,
        rendered: RenderedPrompt,
        model: PromptModel,
    ) -> dict[str, Any]:
        """Adapta un prompt renderizado al formato del modelo."""
        adapter = self._adapters.get(model, self._default)
        return adapter.adapt(rendered)

    def register_adapter(
        self,
        model: PromptModel,
        adapter: ModelAdapter,
    ) -> None:
        """Registra un adaptador para un modelo."""
        self._adapters[model] = adapter


class ModelAdapter:
    """Adaptador base para modelos."""
    
    def adapt(self, rendered: RenderedPrompt) -> dict[str, Any]:
        raise NotImplementedError


class OpenAIAdapter(ModelAdapter):
    """Adaptador para modelos OpenAI."""
    
    def adapt(self, rendered: RenderedPrompt) -> dict[str, Any]:
        return rendered.to_openai_format()


class AnthropicAdapter(ModelAdapter):
    """Adaptador para modelos Anthropic (Claude)."""
    
    def adapt(self, rendered: RenderedPrompt) -> dict[str, Any]:
        return rendered.to_anthropic_format()


class GeminiAdapter(ModelAdapter):
    """Adaptador para modelos Google Gemini."""
    
    def adapt(self, rendered: RenderedPrompt) -> dict[str, Any]:
        return rendered.to_gemini_format()


class LocalModelAdapter(ModelAdapter):
    """Adaptador para modelos locales (Llama, Mistral, etc.)."""
    
    def adapt(self, rendered: RenderedPrompt) -> dict[str, Any]:
        # Formato genérico para modelos locales
        messages = []
        
        if rendered.system_message:
            messages.append({
                "role": "system",
                "content": rendered.system_message,
            })
        
        messages.append({
            "role": "user",
            "content": rendered.user_message,
        })
        
        return {
            "messages": messages,
            "model": rendered.model.value if rendered.model else "local",
            "temperature": 0.7,
            "max_tokens": 2048,
        }
