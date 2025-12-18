"""
Base class and factory for embedding providers.
"""
import time
from abc import ABC, abstractmethod
from typing import List

from ..exceptions import EmbeddingError
from ..logger import get_logger


logger = get_logger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    def __init__(
        self,
        model: str,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize embedding provider.
        
        Args:
            model: Model name
            timeout: API timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text (implementation required).
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        pass
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding with retry logic.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
            
        Raises:
            EmbeddingError: If all retry attempts fail
        """
        delays = [1, 3, 5]
        
        for attempt in range(self.max_retries):
            try:
                return self._generate_embedding(text)
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = delays[attempt]
                    logger.warning(
                        f"Embedding attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    raise EmbeddingError(
                        f"Failed to generate embedding after "
                        f"{self.max_retries} attempts: {e}"
                    )
        
        raise EmbeddingError("Unexpected error in retry logic")


class EmbeddingFactory:
    """Factory for creating embedding providers."""
    
    @staticmethod
    def create(
        provider: str,
        model: str,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> EmbeddingProvider:
        """
        Create embedding provider instance.
        
        Args:
            provider: Provider name (openai, voyageai, gemini, 
                      sentence-transformers)
            model: Model name
            timeout: API timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            EmbeddingProvider instance
            
        Raises:
            EmbeddingError: If provider is not supported
        """
        from .openai_provider import OpenAIProvider
        from .voyageai_provider import VoyageAIProvider
        from .gemini_provider import GeminiProvider
        from .sentence_transformers_provider import (
            SentenceTransformersProvider
        )
        
        providers = {
            "openai": OpenAIProvider,
            "voyageai": VoyageAIProvider,
            "gemini": GeminiProvider,
            "sentence-transformers": SentenceTransformersProvider,
        }
        
        provider_lower = provider.lower()
        if provider_lower not in providers:
            raise EmbeddingError(
                f"Unsupported embedding provider: {provider}. "
                f"Supported: {', '.join(providers.keys())}"
            )
        
        logger.info(f"Creating {provider} embedding provider")
        return providers[provider_lower](model, timeout, max_retries)
