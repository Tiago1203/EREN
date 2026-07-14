"""Model catalog for EREN OS Cognitive Model Registry.

Provides pre-defined model descriptors for common providers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.models.descriptor import ModelDescriptor
from core.models.types import (
    ModelCategory,
    ModelPricing,
    ModelAvailability,
)

if TYPE_CHECKING:
    pass


class ModelCatalog:
    """Catalog of pre-defined model descriptors.

    Contains descriptors for models from various providers.
    These can be used as templates or directly registered.
    """

    # OpenAI Models
    GPT_5 = ModelDescriptor(
        model_id="gpt-5",
        provider_id="openai",
        display_name="GPT-5",
        context_window=128000,
        max_output_tokens=16000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.03, cost_per_output_token=0.06),
        availability=ModelAvailability(rate_limit_per_minute=500),
    )

    GPT_5_MINI = ModelDescriptor(
        model_id="gpt-5-mini",
        provider_id="openai",
        display_name="GPT-5 Mini",
        context_window=64000,
        max_output_tokens=8000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.015, cost_per_output_token=0.03),
        availability=ModelAvailability(rate_limit_per_minute=1000),
    )

    GPT_5_NANO = ModelDescriptor(
        model_id="gpt-5-nano",
        provider_id="openai",
        display_name="GPT-5 Nano",
        context_window=32000,
        max_output_tokens=4000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=False,
        supports_reasoning=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.01, cost_per_output_token=0.02),
        availability=ModelAvailability(rate_limit_per_minute=2000),
    )

    GPT_4_TURBO = ModelDescriptor(
        model_id="gpt-4-turbo",
        provider_id="openai",
        display_name="GPT-4 Turbo",
        context_window=128000,
        max_output_tokens=16000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.01, cost_per_output_token=0.03),
        availability=ModelAvailability(rate_limit_per_minute=500),
    )

    GPT_4O = ModelDescriptor(
        model_id="gpt-4o",
        provider_id="openai",
        display_name="GPT-4o",
        context_window=128000,
        max_output_tokens=16000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.005, cost_per_output_token=0.015),
        availability=ModelAvailability(rate_limit_per_minute=500),
    )

    GPT_4O_MINI = ModelDescriptor(
        model_id="gpt-4o-mini",
        provider_id="openai",
        display_name="GPT-4o Mini",
        context_window=128000,
        max_output_tokens=8000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.00015, cost_per_output_token=0.0006),
        availability=ModelAvailability(rate_limit_per_minute=2000),
    )

    # Claude Models
    CLAUDE_SONNET_4 = ModelDescriptor(
        model_id="claude-sonnet-4",
        provider_id="claude",
        display_name="Claude Sonnet 4",
        context_window=200000,
        max_output_tokens=8000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.003, cost_per_output_token=0.015),
        availability=ModelAvailability(rate_limit_per_minute=400),
    )

    CLAUDE_OPUS_4 = ModelDescriptor(
        model_id="claude-opus-4",
        provider_id="claude",
        display_name="Claude Opus 4",
        context_window=200000,
        max_output_tokens=8000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.REASONING,
        pricing=ModelPricing(cost_per_input_token=0.015, cost_per_output_token=0.075),
        availability=ModelAvailability(rate_limit_per_minute=200),
    )

    CLAUDE_HAIKU_3 = ModelDescriptor(
        model_id="claude-haiku-3",
        provider_id="claude",
        display_name="Claude Haiku 3",
        context_window=200000,
        max_output_tokens=4000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.0008, cost_per_output_token=0.004),
        availability=ModelAvailability(rate_limit_per_minute=2000),
    )

    # Ollama Models (Local)
    LLAMA_3_1_70B = ModelDescriptor(
        model_id="llama3.1:70b",
        provider_id="ollama",
        display_name="Llama 3.1 70B",
        context_window=128000,
        max_output_tokens=4000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=False,
        supports_reasoning=True,
        supports_tools=False,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.0, cost_per_output_token=0.0),  # Local, no API cost
        availability=ModelAvailability(available=True, region="local"),
    )

    LLAMA_3_1_8B = ModelDescriptor(
        model_id="llama3.1:8b",
        provider_id="ollama",
        display_name="Llama 3.1 8B",
        context_window=128000,
        max_output_tokens=4000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=False,
        supports_reasoning=True,
        supports_tools=False,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.0, cost_per_output_token=0.0),
        availability=ModelAvailability(available=True, region="local"),
    )

    MISTRAL_7B = ModelDescriptor(
        model_id="mistral:7b",
        provider_id="ollama",
        display_name="Mistral 7B",
        context_window=32000,
        max_output_tokens=4000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=False,
        supports_reasoning=False,
        supports_tools=False,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.0, cost_per_output_token=0.0),
        availability=ModelAvailability(available=True, region="local"),
    )

    QWEN_2_72B = ModelDescriptor(
        model_id="qwen2:72b",
        provider_id="ollama",
        display_name="Qwen 2 72B",
        context_window=128000,
        max_output_tokens=8000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.0, cost_per_output_token=0.0),
        availability=ModelAvailability(available=True, region="local"),
    )

    # Gemini Models
    GEMINI_2_5_PRO = ModelDescriptor(
        model_id="gemini-2.5-pro",
        provider_id="gemini",
        display_name="Gemini 2.5 Pro",
        context_window=2000000,
        max_output_tokens=32000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.00125, cost_per_output_token=0.005),
        availability=ModelAvailability(rate_limit_per_minute=100),
    )

    GEMINI_2_5_FLASH = ModelDescriptor(
        model_id="gemini-2.5-flash",
        provider_id="gemini",
        display_name="Gemini 2.5 Flash",
        context_window=1000000,
        max_output_tokens=16000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.GENERAL,
        pricing=ModelPricing(cost_per_input_token=0.000075, cost_per_output_token=0.0003),
        availability=ModelAvailability(rate_limit_per_minute=2000),
    )

    # Medical Models
    CLAUDE_MEDICAL = ModelDescriptor(
        model_id="claude-medical",
        provider_id="claude",
        display_name="Claude Medical",
        context_window=200000,
        max_output_tokens=8000,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_multimodal=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_tools=True,
        category=ModelCategory.MEDICAL,
        pricing=ModelPricing(cost_per_input_token=0.015, cost_per_output_token=0.075),
        availability=ModelAvailability(rate_limit_per_minute=100),
    )

    @classmethod
    def get_all_descriptors(cls) -> list[ModelDescriptor]:
        """Get all pre-defined descriptors.

        Returns:
            List of all model descriptors in the catalog.
        """
        return [
            cls.GPT_5,
            cls.GPT_5_MINI,
            cls.GPT_5_NANO,
            cls.GPT_4_TURBO,
            cls.GPT_4O,
            cls.GPT_4O_MINI,
            cls.CLAUDE_SONNET_4,
            cls.CLAUDE_OPUS_4,
            cls.CLAUDE_HAIKU_3,
            cls.LLAMA_3_1_70B,
            cls.LLAMA_3_1_8B,
            cls.MISTRAL_7B,
            cls.QWEN_2_72B,
            cls.GEMINI_2_5_PRO,
            cls.GEMINI_2_5_FLASH,
            cls.CLAUDE_MEDICAL,
        ]

    @classmethod
    def get_by_provider(cls, provider_id: str) -> list[ModelDescriptor]:
        """Get descriptors by provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            List of model descriptors for the provider.
        """
        return [d for d in cls.get_all_descriptors() if d.provider_id == provider_id]

    @classmethod
    def get_by_category(cls, category: ModelCategory) -> list[ModelDescriptor]:
        """Get descriptors by category.

        Args:
            category: Model category.

        Returns:
            List of model descriptors in the category.
        """
        return [d for d in cls.get_all_descriptors() if d.category == category]

    @classmethod
    def get_by_capability(cls, capability: str) -> list[ModelDescriptor]:
        """Get descriptors by capability.

        Args:
            capability: Capability name.

        Returns:
            List of model descriptors with the capability.
        """
        return [d for d in cls.get_all_descriptors() if d.supports_capability(capability)]

    @classmethod
    def get_by_id(cls, model_id: str) -> ModelDescriptor | None:
        """Get descriptor by model ID.

        Args:
            model_id: Model identifier.

        Returns:
            Model descriptor or None.
        """
        for descriptor in cls.get_all_descriptors():
            if descriptor.model_id == model_id:
                return descriptor
        return None
