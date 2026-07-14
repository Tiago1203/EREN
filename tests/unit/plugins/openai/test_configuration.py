"""Unit tests for OpenAI configuration module."""

import pytest

from plugins.openai.configuration import (
    OpenAIConfiguration,
    load_configuration,
    validate_api_key,
)
from plugins.openai.exceptions import OpenAIConfigurationError


class TestOpenAIConfiguration:
    """Tests for OpenAIConfiguration."""

    def test_defaults(self):
        """Test default configuration."""
        config = OpenAIConfiguration()

        assert config.provider == "openai"
        assert config.model == "gpt-5-mini"
        assert config.temperature == 0.2
        assert config.max_tokens == 4000
        assert config.timeout == 60
        assert config.retries == 3
        assert config.stream is False

    def test_custom_values(self):
        """Test custom configuration."""
        config = OpenAIConfiguration(
            model="gpt-4",
            temperature=0.5,
            max_tokens=8000,
        )

        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 8000

    def test_invalid_model(self):
        """Test invalid model raises error."""
        with pytest.raises(OpenAIConfigurationError) as exc_info:
            OpenAIConfiguration(model="invalid-model")

        assert "Unsupported model" in str(exc_info.value)

    def test_invalid_temperature(self):
        """Test invalid temperature raises error."""
        with pytest.raises(OpenAIConfigurationError) as exc_info:
            OpenAIConfiguration(temperature=3.0)

        assert "Temperature must be between 0 and 2" in str(exc_info.value)

    def test_invalid_timeout(self):
        """Test invalid timeout raises error."""
        with pytest.raises(OpenAIConfigurationError) as exc_info:
            OpenAIConfiguration(timeout=0)

        assert "timeout must be positive" in str(exc_info.value)

    def test_invalid_retries(self):
        """Test invalid retries raises error."""
        with pytest.raises(OpenAIConfigurationError) as exc_info:
            OpenAIConfiguration(retries=-1)

        assert "retries must be non-negative" in str(exc_info.value)

    def test_max_tokens_exceeds_model_limit(self):
        """Test max_tokens exceeding model limit."""
        with pytest.raises(OpenAIConfigurationError) as exc_info:
            OpenAIConfiguration(model="gpt-5-nano", max_tokens=10000)

        assert "exceeds model limit" in str(exc_info.value)

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "model": "gpt-4",
            "temperature": 0.7,
            "custom_field": "custom_value",
        }

        config = OpenAIConfiguration.from_dict(data)

        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.metadata["custom_field"] == "custom_value"

    def test_to_dict(self):
        """Test converting to dictionary."""
        config = OpenAIConfiguration(model="gpt-4")

        d = config.to_dict()

        assert d["model"] == "gpt-4"
        assert d["provider"] == "openai"
        assert d["temperature"] == 0.2


class TestLoadConfiguration:
    """Tests for load_configuration."""

    def test_load_none(self):
        """Test loading None returns defaults."""
        config = load_configuration(None)
        assert isinstance(config, OpenAIConfiguration)
        assert config.model == "gpt-5-mini"

    def test_load_dict(self):
        """Test loading from dictionary."""
        config = load_configuration({"model": "gpt-4", "temperature": 0.8})
        assert config.model == "gpt-4"
        assert config.temperature == 0.8


class TestValidateApiKey:
    """Tests for validate_api_key."""

    def test_valid_api_key(self):
        """Test valid API key."""
        assert validate_api_key("sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890") is True

    def test_none_api_key(self):
        """Test None API key raises error."""
        with pytest.raises(ValueError) as exc_info:
            validate_api_key(None)

        assert "API key is required" in str(exc_info.value)

    def test_empty_api_key(self):
        """Test empty API key raises error."""
        with pytest.raises(ValueError) as exc_info:
            validate_api_key("")

        assert "API key is required" in str(exc_info.value)

    def test_invalid_prefix(self):
        """Test invalid prefix raises error."""
        with pytest.raises(ValueError) as exc_info:
            validate_api_key("invalid-key")

        assert "must start with 'sk-'" in str(exc_info.value)

    def test_too_short(self):
        """Test too short key raises error."""
        with pytest.raises(ValueError) as exc_info:
            validate_api_key("sk-short")

        assert "too short" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
