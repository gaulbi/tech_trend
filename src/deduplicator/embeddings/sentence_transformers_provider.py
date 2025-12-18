"""
Sentence Transformers (local) embedding provider implementation.
"""
from typing import List

from sentence_transformers import SentenceTransformer

from .base import EmbeddingProvider


class SentenceTransformersProvider(EmbeddingProvider):
    """Sentence Transformers local embedding provider."""
    
    def __init__(
        self,
        model: str,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize Sentence Transformers provider.
        
        Args:
            model: Model name (e.g., all-MiniLM-L6-v2)
            timeout: Not used for local models
            max_retries: Maximum retry attempts
        """
        super().__init__(model, timeout, max_retries)
        self.model_instance = SentenceTransformer(model)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using local Sentence Transformers model.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        embedding = self.model_instance.encode(
            text,
            convert_to_tensor=False,
        )
        return embedding.tolist()
