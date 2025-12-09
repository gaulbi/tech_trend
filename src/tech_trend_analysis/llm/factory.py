# ============================================================================
# src/tech_trend_analysis/llm/factory.py
# ============================================================================

"""Factory for creating LLM clients."""

from ..config import Config
from ..exceptions import ConfigurationError
from .base import BaseLLMClient
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient
from .claude_client import ClaudeClient
from .ollama_client import OllamaClient


class LLMClientFactory:
    """Factory for creating LLM client instances."""

    @staticmethod
    def create(config: Config) -> BaseLLMClient:
        """
        Create an LLM client based on configuration.

        Args:
            config: Application configuration

        Returns:
            LLM client instance

        Raises:
            ConfigurationError: If provider is unknown
        """
        provider = config.llm_server.lower()
        model = config.llm_model
        timeout = config.llm_timeout
        retry = config.llm_retry

        if provider == 'openai':
            api_key = config.get_api_key('openai')
            return OpenAIClient(api_key, model, timeout, retry)

        elif provider == 'deepseek':
            api_key = config.get_api_key('deepseek')
            return DeepSeekClient(api_key, model, timeout, retry)

        elif provider == 'claude':
            api_key = config.get_api_key('claude')
            return ClaudeClient(api_key, model, timeout, retry)

        elif provider == 'ollama':
            return OllamaClient("", model, timeout, retry)

        else:
            raise ConfigurationError(f"Unknown LLM provider: {provider}")