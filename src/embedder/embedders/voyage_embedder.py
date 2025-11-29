"""Voyage AI embedding provider implementation."""

import os
from typing import List

import voyageai

from ..exceptions import EmbeddingError
from .base import BaseEmbedder


class VoyageEmbedder(BaseEmbedder):
    """Voyage AI embedding provider with retry logic."""

    DIMENSION_MAP = {
        "voyage-large-2": 1536,
        "voyage-code-2": 1536,
        "voyage-2": 1024,
        "voyage-lite-02-instruct": 1024,
    }

    def __init__(
        self, model: str, timeout: int = 60, max_retries: int = 3
    ) -> None:
        """
        Initialize Voyage AI embedder.

        Args:
            model: Voyage model name.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.

        Raises:
            EmbeddingError: If API key is missing.
        """
        super().__init__(model, timeout, max_retries)

        api_key = os.getenv("VOYAGEAI_API_KEY")
        if not api_key:
            raise EmbeddingError("VOYAGEAI_API_KEY not found in environment")

        self.client = voyageai.Client(api_key=api_key)

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Voyage AI API.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.

        Raises:
            EmbeddingError: If API call fails.
        """
        try:
            response = self.client.embed(
                texts=texts, model=self.model, input_type="document"
            )
            return response.embeddings
        except Exception as e:
            raise EmbeddingError(f"Voyage AI API error: {e}") from e

    def get_dimension(self) -> int:
        """
        Get embedding dimension for the model.

        Returns:
            Embedding vector dimension.
        """
        return self.DIMENSION_MAP.get(self.model, 1536)