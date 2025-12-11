"""
Google Gemini embedding provider.
"""

import os
from typing import List

import google.generativeai as genai

from ..exceptions import EmbeddingError
from .base import BaseEmbedder


class GeminiEmbedder(BaseEmbedder):
    """Google Gemini embedding provider."""
    
    # Model dimensions mapping
    DIMENSIONS = {
        'models/embedding-001': 768,
        'models/text-embedding-004': 768,
    }
    
    def __init__(
        self,
        model_name: str = "models/embedding-001",
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize Gemini embedder.
        
        Args:
            model_name: Gemini embedding model name
            timeout: Timeout for API calls in seconds
            max_retries: Maximum number of retry attempts
            
        Raises:
            EmbeddingError: If API key is not found
        """
        super().__init__(model_name, timeout, max_retries)
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise EmbeddingError(
                "GEMINI_API_KEY not found in environment"
            )
        
        genai.configure(api_key=api_key)
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Gemini API.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            embeddings = []
            
            # Gemini API processes one text at a time
            for text in texts:
                result = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            
            return embeddings
            
        except Exception as e:
            raise EmbeddingError(f"Gemini embedding failed: {e}")
    
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension
        """
        return self.DIMENSIONS.get(self.model_name, 768)