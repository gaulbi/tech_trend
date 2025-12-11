"""
Abstract base class for embedding providers.
"""

import time
from abc import ABC, abstractmethod
from typing import List

from ..exceptions import RetryExhaustedError
from ..logger import get_logger


logger = get_logger(__name__)


class BaseEmbedder(ABC):
    """Abstract base class for embedding providers."""
    
    def __init__(
        self,
        model_name: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize embedder.
        
        Args:
            model_name: Name of the embedding model
            timeout: Timeout for API calls in seconds
            max_retries: Maximum number of retry attempts
        """
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass
    
    def embed_with_retry(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings with exponential backoff retry logic.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            RetryExhaustedError: If all retries are exhausted
        """
        retry_delays = [1, 3, 5]  # Exponential backoff delays
        
        for attempt in range(self.max_retries):
            try:
                embeddings = self.embed(texts)
                
                if attempt > 0:
                    logger.info(
                        f"Embedding succeeded on attempt {attempt + 1}"
                    )
                
                return embeddings
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(
                        f"Embedding attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries} embedding attempts failed"
                    )
                    raise RetryExhaustedError(
                        f"Failed after {self.max_retries} attempts: {e}"
                    )
        
        raise RetryExhaustedError(
            f"Failed after {self.max_retries} attempts"
        )
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension
        """
        pass