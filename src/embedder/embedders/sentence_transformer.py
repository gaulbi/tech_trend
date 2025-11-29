"""Sentence Transformers local embedding provider."""

from typing import List

from sentence_transformers import SentenceTransformer

from ..exceptions import EmbeddingError
from .base import BaseEmbedder


class SentenceTransformerEmbedder(BaseEmbedder):
    """Local sentence transformer embedding provider."""

    DIMENSION_MAP = {
        "all-MiniLM-L6-v2": 384,
        "all-mpnet-base-v2": 768,
        "paraphrase-multilingual-MiniLM-L12-v2": 384,
    }

    def __init__(
        self, model: str, timeout: int = 60, max_retries: int = 3
    ) -> None:
        """
        Initialize Sentence Transformer embedder.

        Args:
            model: Model name from sentence-transformers.
            timeout: Not used for local models.
            max_retries: Maximum retry attempts.

        Raises:
            EmbeddingError: If model loading fails.
        """
        super().__init__(model, timeout, max_retries)

        try:
            self.encoder = SentenceTransformer(model)
        except Exception as e:
            raise EmbeddingError(
                f"Failed to load model '{model}': {e}"
            ) from e

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using local model.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.

        Raises:
            EmbeddingError: If encoding fails.
        """
        try:
            embeddings = self.encoder.encode(
                texts, show_progress_bar=False, convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            raise EmbeddingError(f"Encoding error: {e}") from e

    def get_dimension(self) -> int:
        """
        Get embedding dimension for the model.

        Returns:
            Embedding vector dimension.
        """
        return self.DIMENSION_MAP.get(
            self.model, self.encoder.get_sentence_embedding_dimension()
        )