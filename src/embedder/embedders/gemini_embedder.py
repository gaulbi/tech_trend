"""Google Gemini embedding provider implementation."""

import os
from typing import List

import google.generativeai as genai

from ..exceptions import EmbeddingError
from .base import BaseEmbedder


class GeminiEmbedder(BaseEmbedder):
    """Google Gemini embedding provider with retry logic."""

    DIMENSION_MAP = {
        "models/embedding-001": 768,
        "models/text-embedding-004": 768,
    }

    def __init__(
        self, model: str, timeout: int = 60, max_retries: int = 3
    ) -> None:
        """
        Initialize Gemini embedder.

        Args:
            model: Gemini model name.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.

        Raises:
            EmbeddingError: If API key is missing.
        """
        super().__init__(model, timeout, max_retries)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EmbeddingError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=api_key)

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Gemini API.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.

        Raises:
            EmbeddingError: If API call fails.
        """
        try:
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document",
                )
                embeddings.append(result["embedding"])
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Gemini API error: {e}") from e

    def get_dimension(self) -> int:
        """
        Get embedding dimension for the model.

        Returns:
            Embedding vector dimension.
        """
        return self.DIMENSION_MAP.get(self.model, 768)