"""
Sentence Transformers (local) embedding provider.
"""

from typing import List

from sentence_transformers import SentenceTransformer

from ..exceptions import EmbeddingError
from .base import BaseEmbedder


class SentenceTransformerEmbedder(BaseEmbedder):
    """Sentence Transformers local embedding provider."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize Sentence Transformer embedder.
        
        Args:
            model_name: Sentence Transformer model name
            timeout: Timeout for operations (not used for local models)
            max_retries: Maximum number of retry attempts
            
        Raises:
            EmbeddingError: If model loading fails
        """
        super().__init__(model_name, timeout, max_retries)
        
        try:
            self.model = SentenceTransformer(model_name)
            self._dimension = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise EmbeddingError(
                f"Failed to load Sentence Transformer model: {e}"
            )
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Sentence Transformers.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            # Convert numpy arrays to lists
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            raise EmbeddingError(
                f"Sentence Transformer embedding failed: {e}"
            )
    
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension
        """
        return self._dimension