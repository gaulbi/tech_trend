"""
OpenAI embedding provider implementation.
"""
import os
from typing import List

from openai import OpenAI

from .base import EmbeddingProvider
from ..exceptions import EmbeddingError


class OpenAIProvider(EmbeddingProvider):
    """OpenAI embedding provider."""
    
    def __init__(
        self,
        model: str,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Model name (e.g., text-embedding-3-small)
            timeout: API timeout in seconds
            max_retries: Maximum retry attempts
            
        Raises:
            EmbeddingError: If API key is not found
        """
        super().__init__(model, timeout, max_retries)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EmbeddingError(
                "OPENAI_API_KEY not found in environment"
            )
        
        self.client = OpenAI(
            api_key=api_key,
            timeout=timeout,
        )
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using OpenAI API.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding
