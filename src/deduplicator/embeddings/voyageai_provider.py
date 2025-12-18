"""
Voyage AI embedding provider implementation.
"""
import os
from typing import List

import voyageai

from .base import EmbeddingProvider
from ..exceptions import EmbeddingError


class VoyageAIProvider(EmbeddingProvider):
    """Voyage AI embedding provider."""
    
    def __init__(
        self,
        model: str,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize Voyage AI provider.
        
        Args:
            model: Model name
            timeout: API timeout in seconds
            max_retries: Maximum retry attempts
            
        Raises:
            EmbeddingError: If API key is not found
        """
        super().__init__(model, timeout, max_retries)
        
        api_key = os.getenv("VOYAGEAI_API_KEY")
        if not api_key:
            raise EmbeddingError(
                "VOYAGEAI_API_KEY not found in environment"
            )
        
        self.client = voyageai.Client(
            api_key=api_key,
            timeout=timeout,
        )
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Voyage AI API.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        result = self.client.embed(
            texts=[text],
            model=self.model,
        )
        return result.embeddings[0]
