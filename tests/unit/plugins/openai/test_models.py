"""Unit tests for OpenAI models module."""

import pytest

from plugins.openai.models import (
    OpenAIModel,
    ModelConfig,
    MODEL_CONFIGS,
    get_model_config,
    get_default_max_tokens,
)


class TestOpenAIModel:
    """Tests for OpenAIModel."""

    def test_values(self):
        """Test model enum values."""
        assert OpenAIModel.GPT_5.value == "gpt-5"
        assert OpenAIModel.GPT_5_MINI.value == "gpt-5-mini"
        assert OpenAIModel.GPT_5_NANO.value == "gpt-5-nano"

    def test_is_supported(self):
        """Test is_supported check."""
        assert OpenAIModel.is_supported("gpt-5") is True
        assert OpenAIModel.is_supported("gpt-4") is True
        assert OpenAIModel.is_supported("gpt-5-mini") is True
        assert OpenAIModel.is_supported("invalid-model") is False

    def test_default(self):
        """Test default model."""
        assert OpenAIModel.default() == OpenAIModel.GPT_5_MINI


class TestModelConfig:
    """Tests for ModelConfig."""

    def test_creation(self):
        """Test model config creation."""
        config = ModelConfig(
            name="gpt-4",
            max_tokens=8000,
            supports_vision=False,
        )

        assert config.name == "gpt-4"
        assert config.max_tokens == 8000
        assert config.supports_vision is False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = ModelConfig(name="gpt-4")
        d = config.to_dict()

        assert d["name"] == "gpt-4"
        assert "max_tokens" in d
        assert "supports_vision" in d


class TestModelConfigs:
    """Tests for MODEL_CONFIGS."""

    def test_gpt5_config(self):
        """Test GPT-5 configuration."""
        config = MODEL_CONFIGS["gpt-5"]
        assert config.name == "gpt-5"
        assert config.context_window == 128000
        assert config.supports_vision is True

    def test_gpt5_mini_config(self):
        """Test GPT-5-mini configuration."""
        config = MODEL_CONFIGS["gpt-5-mini"]
        assert config.name == "gpt-5-mini"
        assert config.context_window == 64000
        assert config.cost_per_input_token == 0.00015

    def test_gpt5_nano_config(self):
        """Test GPT-5-nano configuration."""
        config = MODEL_CONFIGS["gpt-5-nano"]
        assert config.name == "gpt-5-nano"
        assert config.supports_vision is False


class TestGetModelConfig:
    """Tests for get_model_config."""

    def test_valid_model(self):
        """Test getting valid model config."""
        config = get_model_config("gpt-4")
        assert config.name == "gpt-4"

    def test_invalid_model(self):
        """Test getting invalid model raises error."""
        with pytest.raises(ValueError) as exc_info:
            get_model_config("invalid-model")

        assert "Unsupported model" in str(exc_info.value)


class TestGetDefaultMaxTokens:
    """Tests for get_default_max_tokens."""

    def test_gpt5(self):
        """Test GPT-5 default max tokens."""
        assert get_default_max_tokens("gpt-5") == 16000

    def test_gpt5_mini(self):
        """Test GPT-5-mini default max tokens."""
        assert get_default_max_tokens("gpt-5-mini") == 8000

    def test_unknown_model(self):
        """Test unknown model returns default."""
        assert get_default_max_tokens("unknown") == 4000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
