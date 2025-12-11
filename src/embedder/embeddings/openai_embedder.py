"""
OpenAI embedding provider.
"""

import os
from typing import List

from openai import OpenAI

from ..exceptions import EmbeddingError
from .base import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI embedding provider."""
    
    # Model dimensions mapping
    DIMENSIONS = {
        'text-embedding-3-small': 1536,
        'text-embedding-3-large': 3072,
        'text-embedding-ada-002': 1536,
    }
    
    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize OpenAI embedder.
        
        Args:
            model_name: OpenAI embedding model name
            timeout: Timeout for API calls in seconds
            max_retries: Maximum number of retry attempts
            
        Raises:
            EmbeddingError: If API key is not found
        """
        super().__init__(model_name, timeout, max_retries)
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise EmbeddingError(
                "OPENAI_API_KEY not found in environment"
            )
        
        self.client = OpenAI(api_key=api_key, timeout=timeout)
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings
            
        except Exception as e:
            raise EmbeddingError(f"OpenAI embedding failed: {e}")
    
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension
        """
        return self.DIMENSIONS.get(self.model_name, 1536)