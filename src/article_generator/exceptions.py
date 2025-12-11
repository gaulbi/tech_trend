# ============================================================================
# src/article_generator/exceptions.py
# ============================================================================
"""Custom exceptions for the article generator."""


class ArticleGeneratorError(Exception):
    """Base exception for article generator."""
    pass


class ConfigurationError(ArticleGeneratorError):
    """Raised when configuration is invalid or missing."""
    pass


class EmbeddingError(ArticleGeneratorError):
    """Raised when embedding operations fail."""
    pass


class LLMError(ArticleGeneratorError):
    """Raised when LLM operations fail."""
    pass


class RAGError(ArticleGeneratorError):
    """Raised when RAG operations fail."""
    pass