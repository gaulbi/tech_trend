"""Factory for creating LLM clients."""

from typing import Dict, Type

from ..exceptions import LLMProviderError
from .base import BaseLLMClient
from .claude_client import ClaudeClient
from .deepseek_client import DeepSeekClient
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient


class LLMClientFactory:
    """Factory for creating LLM client instances."""
    
    _PROVIDERS: Dict[str, Type[BaseLLMClient]] = {
        "openai": OpenAIClient,
        "deepseek": DeepSeekClient,
        "claude": ClaudeClient,
        "ollama": OllamaClient
    }
    
    @classmethod
    def create(cls, provider: str, model: str, 
               timeout: int, max_retries: int) -> BaseLLMClient:
        """
        Create an LLM client instance.
        
        Args:
            provider: Provider name (openai, deepseek, claude, ollama)
            model: Model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            
        Returns:
            Configured LLM client instance
            
        Raises:
            LLMProviderError: If provider is not supported
        """
        provider_lower = provider.lower()
        client_class = cls._PROVIDERS.get(provider_lower)
        
        if not client_class:
            supported = ", ".join(cls._PROVIDERS.keys())
            raise LLMProviderError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {supported}"
            )
        
        return client_class(model, timeout, max_retries)