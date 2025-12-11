"""
Voyage AI embedding provider.
"""

import os
from typing import List

import voyageai

from ..exceptions import EmbeddingError
from .base import BaseEmbedder


class VoyageEmbedder(BaseEmbedder):
    """Voyage AI embedding provider."""
    
    # Model dimensions mapping
    DIMENSIONS = {
        'voyage-2': 1024,
        'voyage-large-2': 1536,
        'voyage-code-2': 1536,
        'voyage-lite-02-instruct': 1024,
    }
    
    def __init__(
        self,
        model_name: str = "voyage-2",
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize Voyage AI embedder.
        
        Args:
            model_name: Voyage AI embedding model name
            timeout: Timeout for API calls in seconds
            max_retries: Maximum number of retry attempts
            
        Raises:
            EmbeddingError: If API key is not found
        """
        super().__init__(model_name, timeout, max_retries)
        
        api_key = os.getenv('VOYAGEAI_API_KEY')
        if not api_key:
            raise EmbeddingError(
                "VOYAGEAI_API_KEY not found in environment"
            )
        
        self.client = voyageai.Client(api_key=api_key)
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Voyage AI API.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model_name
            )
            
            return response.embeddings
            
        except Exception as e:
            raise EmbeddingError(f"Voyage AI embedding failed: {e}")
    
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension
        """
        return self.DIMENSIONS.get(self.model_name, 1024)