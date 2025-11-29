"""Factory for creating embedding provider instances."""

from typing import Dict, Type

from ..exceptions import EmbeddingError
from .base import BaseEmbedder
from .gemini_embedder import GeminiEmbedder
from .openai_embedder import OpenAIEmbedder
from .sentence_transformer import SentenceTransformerEmbedder
from .voyage_embedder import VoyageEmbedder


class EmbedderFactory:
    """Factory for creating embedding provider instances."""

    _providers: Dict[str, Type[BaseEmbedder]] = {
        "openai": OpenAIEmbedder,
        "voyageai": VoyageEmbedder,
        "gemini": GeminiEmbedder,
        "sentence-transformers": SentenceTransformerEmbedder,
    }

    @classmethod
    def create(
        cls, provider: str, model: str, timeout: int, max_retries: int
    ) -> BaseEmbedder:
        """
        Create an embedder instance based on provider name.

        Args:
            provider: Provider name (openai, voyageai, gemini, etc).
            model: Model identifier.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.

        Returns:
            Configured embedder instance.

        Raises:
            EmbeddingError: If provider is not supported.
        """
        provider_lower = provider.lower()

        if provider_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise EmbeddingError(
                f"Unsupported provider '{provider}'. "
                f"Available: {available}"
            )

        embedder_class = cls._providers[provider_lower]
        return embedder_class(
            model=model, timeout=timeout, max_retries=max_retries
        )

    @classmethod
    def register_provider(
        cls, name: str, embedder_class: Type[BaseEmbedder]
    ) -> None:
        """
        Register a custom embedding provider.

        Args:
            name: Provider name identifier.
            embedder_class: Class implementing BaseEmbedder.
        """
        cls._providers[name.lower()] = embedder_class