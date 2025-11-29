"""Factory for creating LLM client instances."""

from .base import BaseLLMClient
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient
from .claude_client import ClaudeClient
from .ollama_client import OllamaClient
from ..exceptions import ConfigurationError


class LLMFactory:
    """Factory class for creating LLM client instances."""

    @staticmethod
    def create_client(
        provider: str,
        api_key: str,
        model: str,
        timeout: int,
        retry_count: int
    ) -> BaseLLMClient:
        """Create LLM client based on provider.
        
        Args:
            provider: Provider name (openai, deepseek, claude, ollama)
            api_key: API key for authentication
            model: Model name to use
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
            
        Returns:
            LLM client instance
            
        Raises:
            ConfigurationError: If provider is not supported
        """
        provider_lower = provider.lower()
        
        if provider_lower == "openai":
            return OpenAIClient(api_key, model, timeout, retry_count)
        elif provider_lower == "deepseek":
            return DeepSeekClient(api_key, model, timeout, retry_count)
        elif provider_lower == "claude":
            return ClaudeClient(api_key, model, timeout, retry_count)
        elif provider_lower == "ollama":
            return OllamaClient(api_key, model, timeout, retry_count)
        else:
            raise ConfigurationError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: openai, deepseek, claude, ollama"
            )