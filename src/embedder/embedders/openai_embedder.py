"""OpenAI embedding provider implementation."""

import os
from typing import List

from openai import OpenAI

from ..exceptions import EmbeddingError
from .base import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI embedding provider with retry logic."""

    DIMENSION_MAP = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(
        self, model: str, timeout: int = 60, max_retries: int = 3
    ) -> None:
        """
        Initialize OpenAI embedder.

        Args:
            model: OpenAI model name.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.

        Raises:
            EmbeddingError: If API key is missing.
        """
        super().__init__(model, timeout, max_retries)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EmbeddingError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key, timeout=timeout)

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.

        Raises:
            EmbeddingError: If API call fails.
        """
        try:
            response = self.client.embeddings.create(
                model=self.model, input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise EmbeddingError(f"OpenAI API error: {e}") from e

    def get_dimension(self) -> int:
        """
        Get embedding dimension for the model.

        Returns:
            Embedding vector dimension.
        """
        return self.DIMENSION_MAP.get(self.model, 1536)