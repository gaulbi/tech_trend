"""
Embedding Client Base Module

Abstract base class and factory for embedding clients.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import time
import logging

logger = logging.getLogger(__name__)


class EmbeddingClientBase(ABC):
    """Abstract base class for embedding clients."""
    
    def __init__(self, model: str, timeout: int = 60, max_retries: int = 3):
        """
        Initialize embedding client.
        
        Args:
            model: Model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        pass
    
    def embed_query_with_retry(self, text: str) -> List[float]:
        """
        Generate embedding with exponential backoff retry logic.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
            
        Raises:
            Exception: If all retries fail
        """
        delays = [1, 3, 5]
        
        for attempt in range(self.max_retries):
            try:
                return self.embed_query(text)
            
            except Exception as e:
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    delay = delays[attempt]
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} embedding attempts failed")
                    raise


class EmbeddingClientFactory:
    """Factory for creating embedding clients."""
    
    @staticmethod
    def create_client(
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ) -> EmbeddingClientBase:
        """
        Create embedding client based on provider.
        
        Args:
            provider: Embedding provider name
            model: Model identifier
            api_key: API key (not needed for local models)
            timeout: Request timeout
            max_retries: Maximum retry attempts
            
        Returns:
            Embedding client instance
            
        Raises:
            ValueError: If provider is unknown
        """
        from src.article_generator.embedding_clients import (
            OpenAIEmbeddingClient,
            VoyageEmbeddingClient,
            GeminiEmbeddingClient,
            SentenceTransformerClient
        )
        
        provider = provider.lower()
        
        if provider == 'openai':
            return OpenAIEmbeddingClient(model, api_key, timeout, max_retries)
        elif provider == 'voyage':
            return VoyageEmbeddingClient(model, api_key, timeout, max_retries)
        elif provider == 'gemini':
            return GeminiEmbeddingClient(model, api_key, timeout, max_retries)
        elif provider == 'sentence-transformers':
            return SentenceTransformerClient(model, timeout, max_retries)
        else:
            raise ValueError(
                f"Unknown embedding provider: {provider}. "
                f"Supported: openai, voyage, gemini, sentence-transformers"
            )