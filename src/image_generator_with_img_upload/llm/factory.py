"""
Factory for creating LLM provider instances.
"""
from typing import Dict, Any

from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .deepseek_provider import DeepSeekProvider
from .gemini_provider import GeminiProvider
from ..exceptions import ConfigurationError


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    PROVIDERS = {
        'OpenAI': {
            'class': OpenAIProvider,
            'env_key': 'OPENAI_IMG_API_KEY'
        },
        'Deepseek': {
            'class': DeepSeekProvider,
            'env_key': 'DEEPSEEK_IMG_API_KEY'
        },
        'Gemini': {
            'class': GeminiProvider,
            'env_key': 'GEMINI_IMG_API_KEY'
        }
    }
    
    @classmethod
    def create(
        cls,
        provider_name: str,
        model: str,
        config: Any
    ) -> BaseLLMProvider:
        """
        Create LLM provider instance.
        
        Args:
            provider_name: Name of the provider (OpenAI, Deepseek, Gemini)
            model: Model name to use
            config: Configuration manager instance
            
        Returns:
            LLM provider instance
            
        Raises:
            ConfigurationError: If provider is not supported or API key missing
        """
        if provider_name not in cls.PROVIDERS:
            raise ConfigurationError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Available: {list(cls.PROVIDERS.keys())}"
            )
        
        provider_info = cls.PROVIDERS[provider_name]
        env_key = provider_info['env_key']
        
        api_key = config.get_env(env_key)
        if not api_key:
            raise ConfigurationError(
                f"Missing API key for {provider_name}. "
                f"Set {env_key} in .env file"
            )
        
        provider_config = cls._build_provider_config(config)
        
        provider_class = provider_info['class']
        return provider_class(api_key, model, provider_config)
    
    @classmethod
    def _build_provider_config(cls, config: Any) -> Dict[str, Any]:
        """Build provider configuration dictionary."""
        return {
            'timeout': config.get('image-generator.timeout', 60),
            'default-size': config.get('image-generator.default-size', 1024),
            'aspect-ratio': config.get('image-generator.aspect-ratio', '1:1'),
            'style-instruction': config.get(
                'image-generator.style-instruction',
                ''
            ),
            'output-format': config.get('image-generator.output-format', 'jpg')
        }
