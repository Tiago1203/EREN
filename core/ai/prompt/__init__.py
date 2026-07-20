"""EREN AI Prompt - Prompt Builder Module.

Módulo de construcción de prompts del AI Core.

## Componentes

- **models**: Modelos de datos (PromptTemplate, RenderedPrompt, etc.)
- **renderer**: Renderizador de prompts
- **optimizer**: Optimizador de prompts
- **versioning**: Versionado de prompts
- **strategy**: Estrategias de prompt

## Modelos Soportados

- GPT (OpenAI): gpt-4, gpt-4-turbo, gpt-3.5-turbo
- Claude (Anthropic): claude-3-opus, claude-3-sonnet, claude-3-haiku
- Gemini (Google): gemini-pro, gemini-ultra
- Modelos Locales: llama-2, mistral

## Estrategias Soportadas

- Direct: Pregunta directa
- Chain of Thought (CoT): Razonamiento paso a paso
- Few-Shot: Con ejemplos
- Tree of Thought (ToT): Múltiples caminos
- ReAct: Reason + Act
- Self-Ask: Preguntas intermedias

## Uso

```python
from core.ai.prompt import (
    PromptBuilder,
    PromptRenderer,
    PromptOptimizer,
    PromptTemplate,
    PromptStrategyType,
    PromptModel,
)

# Crear template
template = PromptTemplate(
    id="support-assistant",
    name="Support Assistant",
    system_template="Eres un asistente de soporte técnico.",
    user_template="Usuario pregunta: {{question}}",
)

# Renderizar
renderer = PromptRenderer()
prompt = renderer.render(template, {"question": "¿Cómo reseteo?"})

# Optimizar
optimizer = PromptOptimizer()
optimized = optimizer.optimize_rendered(prompt)
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     PROMPT BUILDER                                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Prompt Templates                          │ │
│  │           system, user, variables, examples               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Strategy Selector                       │ │
│  │       Direct │ CoT │ Few-Shot │ ToT │ ReAct │ etc.       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Prompt Renderer                         │ │
│  │                 Template + Variables = Prompt               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Prompt Optimizer                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Model Adapter                           │ │
│  │          OpenAI │ Anthropic │ Gemini │ Local              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Prompt Versioning                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```
"""

from core.ai.prompt.models import (
    PromptModel,
    PromptRole,
    PromptStrategyType,
    PromptTemplate,
    PromptVariable,
    PromptExample,
    RenderedPrompt,
    PromptConfig,
)
from core.ai.prompt.renderer import (
    PromptRenderer,
    ModelPromptAdapter,
    ModelAdapter,
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    LocalModelAdapter,
)
from core.ai.prompt.optimizer import (
    PromptOptimizer,
    PromptAnalyzer,
    PromptAnalysis,
)
from core.ai.prompt.versioning import (
    PromptVersion,
    PromptVersionHistory,
    PromptVersioningManager,
    VersionStatus,
)
from core.ai.prompt.strategy import (
    PromptStrategy,
    DirectStrategy,
    ChainOfThoughtStrategy,
    FewShotStrategy,
    TreeOfThoughtStrategy,
    ReActStrategy,
    SelfAskStrategy,
    StrategyFactory,
)


class PromptBuilder:
    """
    Builder principal de prompts.
    
    Combina todas las funcionalidades de prompt
    en una interfaz unificada.
    """

    def __init__(
        self,
        config: PromptConfig | None = None,
    ) -> None:
        self.config = config or PromptConfig()
        self.renderer = PromptRenderer(
            default_model=self.config.default_model,
        )
        self.optimizer = PromptOptimizer()
        self.analyzer = PromptAnalyzer()
        self.versioning = PromptVersioningManager()
        self.strategy_factory = StrategyFactory()
        self.model_adapter = ModelPromptAdapter()

    def build(
        self,
        template: PromptTemplate,
        variables: dict[str, Any],
        strategy: PromptStrategyType | None = None,
        optimize: bool = True,
        target_model: PromptModel | None = None,
    ) -> RenderedPrompt:
        """
        Construye un prompt.
        
        Args:
            template: Template de prompt
            variables: Variables de template
            strategy: Estrategia a usar
            optimize: Si aplicar optimización
            target_model: Modelo destino
            
        Returns:
            Prompt renderizado
        """
        # Renderizar con estrategia
        if strategy:
            prompt = self.renderer.render(template, variables, strategy)
        else:
            prompt = self.renderer.render(template, variables)
        
        # Optimizar si está habilitado
        if optimize and self.config.enable_optimization:
            prompt = self.optimizer.optimize_rendered(prompt)
        
        # Adaptar a modelo si se especifica
        if target_model:
            prompt.model = target_model
        
        return prompt

    def analyze(self, text: str) -> PromptAnalysis:
        """Analiza un prompt."""
        return self.analyzer.analyze(text)

    def version(
        self,
        template: PromptTemplate,
        description: str = "",
        created_by: str | None = None,
    ) -> PromptVersion:
        """Crea una nueva versión del template."""
        return self.versioning.create_version(
            template_id=template.id,
            system_template=template.system_template,
            user_template=template.user_template,
            created_by=created_by,
            description=description,
            set_active=True,
        )

    def get_best_prompt(
        self,
        template_id: str,
        metric: str = "success_rate",
    ) -> PromptVersion | None:
        """Obtiene la mejor versión de un template."""
        return self.versioning.get_best_version(template_id, metric)


__version__ = "1.0.0"

__all__ = [
    # Main builder
    "PromptBuilder",
    # Models
    "PromptModel",
    "PromptRole",
    "PromptStrategyType",
    "PromptTemplate",
    "PromptVariable",
    "PromptExample",
    "RenderedPrompt",
    "PromptConfig",
    # Renderer
    "PromptRenderer",
    "ModelPromptAdapter",
    "ModelAdapter",
    "OpenAIAdapter",
    "AnthropicAdapter",
    "GeminiAdapter",
    "LocalModelAdapter",
    # Optimizer
    "PromptOptimizer",
    "PromptAnalyzer",
    "PromptAnalysis",
    # Versioning
    "PromptVersion",
    "PromptVersionHistory",
    "PromptVersioningManager",
    "VersionStatus",
    # Strategy
    "PromptStrategy",
    "DirectStrategy",
    "ChainOfThoughtStrategy",
    "FewShotStrategy",
    "TreeOfThoughtStrategy",
    "ReActStrategy",
    "SelfAskStrategy",
    "StrategyFactory",
]
