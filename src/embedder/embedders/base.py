"""Abstract base class for embedding providers."""

import time
from abc import ABC, abstractmethod
from typing import List

from ..exceptions import EmbeddingError


class BaseEmbedder(ABC):
    """Abstract base class for all embedding providers."""

    def __init__(
        self, model: str, timeout: int = 60, max_retries: int = 3
    ) -> None:
        """
        Initialize embedder with retry logic.

        Args:
            model: Model identifier for the provider.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors.

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        pass

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings with retry logic.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors.

        Raises:
            EmbeddingError: If all retry attempts fail.
        """
        if not texts:
            return []

        retry_delays = [1, 3, 5]  # Exponential backoff delays

        for attempt in range(self.max_retries):
            try:
                return self._embed_batch(texts)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise EmbeddingError(
                        f"Failed after {self.max_retries} attempts: {e}"
                    ) from e

                delay = retry_delays[attempt]
                time.sleep(delay)

        # Should never reach here
        raise EmbeddingError("Unexpected error in retry logic")

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimensionality of embeddings.

        Returns:
            Embedding vector dimension.
        """
        pass