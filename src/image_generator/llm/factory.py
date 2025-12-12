"""
Factory for creating LLM provider instances.
"""
import os
from typing import Dict, Type
from dotenv import load_dotenv

from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .deepseek_provider import DeepSeekProvider
from .gemini_provider import GeminiProvider
from ..exceptions import ConfigurationError


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider,
        "gemini": GeminiProvider
    }
    
    _api_key_map = {
        "openai": "OPENAI_IMG_API_KEY",
        "deepseek": "DEEPSEEK_IMG_API_KEY",
        "gemini": "GEMINI_IMG_API_KEY"
    }
    
    @classmethod
    def create(
        cls,
        provider: str,
        model: str,
        timeout: int = 60,
        retry: int = 3
    ) -> BaseLLMProvider:
        """
        Create LLM provider instance.
        
        Args:
            provider: Provider name (OpenAI, DeepSeek, Gemini)
            model: Model name
            timeout: Request timeout
            retry: Retry attempts
            
        Returns:
            LLM provider instance
            
        Raises:
            ConfigurationError: If provider is invalid or API key missing
        """
        # Load environment variables
        load_dotenv()
        
        provider_lower = provider.lower()
        
        if provider_lower not in cls._providers:
            raise ConfigurationError(
                f"Unknown provider: {provider}. "
                f"Available: {', '.join(cls._providers.keys())}"
            )
        
        # Get API key
        api_key_env = cls._api_key_map.get(provider_lower)
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ConfigurationError(
                f"API key not found for {provider}. "
                f"Please set {api_key_env} in .env file"
            )
        
        provider_class = cls._providers[provider_lower]
        return provider_class(
            api_key=api_key,
            model=model,
            timeout=timeout,
            retry=retry
        )
