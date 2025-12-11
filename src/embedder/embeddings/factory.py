"""
Factory for creating embedding providers.
"""

from typing import Dict, Any

from ..exceptions import ConfigurationError
from .base import BaseEmbedder
from .openai_embedder import OpenAIEmbedder
from .voyage_embedder import VoyageEmbedder
from .gemini_embedder import GeminiEmbedder
from .sentence_transformer import SentenceTransformerEmbedder


class EmbedderFactory:
    """Factory for creating embedding providers."""
    
    @staticmethod
    def create(config: Dict[str, Any]) -> BaseEmbedder:
        """
        Create an embedder instance based on configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Embedder instance
            
        Raises:
            ConfigurationError: If provider is not supported
        """
        provider = config['embedding']['embedding-provider'].lower()
        model_name = config['embedding']['embedding-model']
        timeout = config['embedding'].get('timeout', 60)
        max_retries = config['embedding'].get('max-retries', 3)
        
        if provider == 'openai':
            return OpenAIEmbedder(
                model_name=model_name,
                timeout=timeout,
                max_retries=max_retries
            )
        
        elif provider == 'voyageai':
            return VoyageEmbedder(
                model_name=model_name,
                timeout=timeout,
                max_retries=max_retries
            )
        
        elif provider == 'gemini':
            return GeminiEmbedder(
                model_name=model_name,
                timeout=timeout,
                max_retries=max_retries
            )
        
        elif provider == 'sentence-transformers':
            return SentenceTransformerEmbedder(
                model_name=model_name,
                timeout=timeout,
                max_retries=max_retries
            )
        
        else:
            raise ConfigurationError(
                f"Unsupported embedding provider: {provider}. "
                f"Supported: openai, voyageai, gemini, sentence-transformers"
            )