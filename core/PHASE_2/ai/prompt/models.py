"""Prompt Models - Modelos de prompt."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PromptModel(str, Enum):
    """Modelos de LLM soportados."""
    # OpenAI
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    CLAUDE_2_1 = "claude-2.1"
    CLAUDE_2 = "claude-2"
    
    # Google
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"
    
    # Local/Other
    LLAMA_2 = "llama-2"
    MISTRAL = "mistral"
    CUSTOM = "custom"


class PromptRole(str, Enum):
    """Roles de mensaje en prompts."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class PromptStrategyType(str, Enum):
    """Tipos de estrategia de prompt."""
    DIRECT = "direct"  # Pregunta directa
    CHAIN_OF_THOUGHT = "cot"  # Chain of thought
    FEW_SHOT = "few_shot"  # Few-shot learning
    ZERO_SHOT = "zero_shot"  # Sin ejemplos
    TREE_OF_THOUGHT = "tot"  # Tree of thought
    REACT = "react"  # ReAct (Reason + Act)
    SELF_ASK = "self_ask"  # Self-ask
    REFLEXION = "reflexion"  # Reflexion


@dataclass
class PromptVariable:
    """Variable en un template de prompt."""
    name: str
    type: str  # string, int, float, bool, list, dict
    description: str = ""
    default: Any = None
    required: bool = True
    validation: dict[str, Any] | None = None


@dataclass
class PromptExample:
    """Ejemplo para few-shot learning."""
    input: str
    output: str
    explanation: str | None = None


@dataclass
class PromptTemplate:
    """Template de prompt."""
    id: str
    name: str
    version: int = 1
    description: str = ""
    strategy: PromptStrategyType = PromptStrategyType.DIRECT
    
    # Componentes del prompt
    system_template: str = ""
    user_template: str = ""
    
    # Variables del template
    variables: list[PromptVariable] = field(default_factory=list)
    
    # Few-shot examples
    examples: list[PromptExample] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Configuración
    max_tokens: int = 4096
    temperature: float = 0.7
    model: PromptModel | None = None
    
    def get_variable(self, name: str) -> PromptVariable | None:
        """Obtiene una variable por nombre."""
        for var in self.variables:
            if var.name == name:
                return var
        return None
    
    def validate_variables(self, values: dict[str, Any]) -> tuple[bool, list[str]]:
        """Valida los valores de las variables."""
        errors = []
        
        for var in self.variables:
            if var.required and var.name not in values:
                errors.append(f"Variable '{var.name}' es requerida")
                continue
            
            if var.name in values:
                value = values[var.name]
                
                # Type validation
                if var.type == "int" and not isinstance(value, int):
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        errors.append(f"Variable '{var.name}' debe ser int")
                
                elif var.type == "float" and not isinstance(value, (int, float)):
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors.append(f"Variable '{var.name}' debe ser float")
                
                elif var.type == "str" and not isinstance(value, str):
                    errors.append(f"Variable '{var.name}' debe ser str")
                
                elif var.type == "bool" and not isinstance(value, bool):
                    errors.append(f"Variable '{var.name}' debe ser bool")
                
                # Custom validation
                if var.validation and errors == []:
                    value = values[var.name]
                    for rule, rule_value in var.validation.items():
                        if rule == "min" and value < rule_value:
                            errors.append(f"'{var.name}' debe ser >= {rule_value}")
                        elif rule == "max" and value > rule_value:
                            errors.append(f"'{var.name}' debe ser <= {rule_value}")
                        elif rule == "min_length" and len(str(value)) < rule_value:
                            errors.append(f"'{var.name}' debe tener >= {rule_value} caracteres")
        
        return len(errors) == 0, errors


@dataclass
class RenderedPrompt:
    """Prompt renderizado listo para usar."""
    user_message: str
    system_message: str | None = None
    assistant_message: str | None = None
    
    # Metadatos
    model: PromptModel | None = None
    tokens_estimate: int = 0
    render_time_ms: float = 0.0
    template_id: str | None = None
    template_version: int | None = None
    
    # Conversión a formato de API
    def to_messages(self) -> list[dict[str, str]]:
        """Convierte a formato de mensajes de API."""
        messages = []
        
        if self.system_message:
            messages.append({
                "role": "system",
                "content": self.system_message,
            })
        
        messages.append({
            "role": "user",
            "content": self.user_message,
        })
        
        if self.assistant_message:
            messages.append({
                "role": "assistant",
                "content": self.assistant_message,
            })
        
        return messages
    
    def to_openai_format(self) -> dict[str, Any]:
        """Convierte a formato OpenAI."""
        return {
            "messages": self.to_messages(),
            "model": self.model.value if self.model else None,
        }
    
    def to_anthropic_format(self) -> dict[str, Any]:
        """Convierte a formato Anthropic."""
        messages = []
        
        if self.system_message:
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": self.system_message}],
            })
        
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": self.user_message}],
        })
        
        return {
            "messages": messages,
            "model": self.model.value if self.model else None,
        }
    
    def to_gemini_format(self) -> dict[str, Any]:
        """Convierte a formato Gemini."""
        contents = []
        
        if self.system_message:
            contents.append({
                "role": "user",
                "parts": [{"text": self.system_message}],
            })
        
        contents.append({
            "role": "user",
            "parts": [{"text": self.user_message}],
        })
        
        return {
            "contents": contents,
            "model": self.model.value if self.model else None,
        }


@dataclass
class PromptConfig:
    """Configuración global de prompts."""
    default_model: PromptModel = PromptModel.GPT_4
    default_temperature: float = 0.7
    default_max_tokens: int = 4096
    max_examples: int = 5
    enable_versioning: bool = True
    enable_optimization: bool = True
    cache_enabled: bool = True
