# ============================================================================
# src/article_generator/clients/factories.py
# ============================================================================
"""Factory classes for creating clients."""
from typing import Dict, Type
from .base import BaseLLMClient, BaseEmbeddingClient
from .llm_clients import (
    OpenAIClient, DeepSeekClient, ClaudeClient, OllamaClient
)
from .embedding_clients import (
    OpenAIEmbedding, VoyageAIEmbedding,
    GeminiEmbedding, SentenceTransformersEmbedding
)
from ..config import Config
from ..exceptions import ConfigurationError


class LLMFactory:
    """Factory for creating LLM clients."""
    
    _clients: Dict[str, Type[BaseLLMClient]] = {
        'openai': OpenAIClient,
        'deepseek': DeepSeekClient,
        'claude': ClaudeClient,
        'ollama': OllamaClient
    }
    
    @classmethod
    def create(cls, config: Config) -> BaseLLMClient:
        """
        Create LLM client from configuration.
        
        Args:
            config: Configuration instance
            
        Returns:
            LLM client instance
            
        Raises:
            ConfigurationError: If provider unknown
        """
        provider = config.get('llm.server', '').lower()
        client_class = cls._clients.get(provider)
        
        if not client_class:
            raise ConfigurationError(f"Unknown LLM provider: {provider}")
        
        model = config.get('llm.llm-model')
        timeout = config.get('llm.timeout', 60)
        max_retries = config.get('llm.retry', 3)
        
        if provider == 'ollama':
            return client_class(
                model=model,
                timeout=timeout,
                max_retries=max_retries
            )
        else:
            api_key = config.get_api_key(provider)
            return client_class(
                api_key=api_key,
                model=model,
                timeout=timeout,
                max_retries=max_retries
            )


class EmbeddingFactory:
    """Factory for creating embedding clients."""
    
    _clients: Dict[str, Type[BaseEmbeddingClient]] = {
        'openai': OpenAIEmbedding,
        'voyageai': VoyageAIEmbedding,
        'gemini': GeminiEmbedding,
        'sentence-transformers': SentenceTransformersEmbedding
    }
    
    @classmethod
    def create(cls, config: Config) -> BaseEmbeddingClient:
        """
        Create embedding client from configuration.
        
        Args:
            config: Configuration instance
            
        Returns:
            Embedding client instance
            
        Raises:
            ConfigurationError: If provider unknown
        """
        provider = config.get('embedding.embedding-provider', '').lower()
        client_class = cls._clients.get(provider)
        
        if not client_class:
            raise ConfigurationError(
                f"Unknown embedding provider: {provider}"
            )
        
        model = config.get('embedding.embedding-model')
        timeout = config.get('embedding.timeout', 60)
        max_retries = config.get('embedding.max-retries', 3)
        
        if provider == 'sentence-transformers':
            return client_class(model=model)
        else:
            api_key = config.get_api_key(provider)
            return client_class(
                api_key=api_key,
                model=model,
                timeout=timeout,
                max_retries=max_retries
            )
