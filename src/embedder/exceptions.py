"""
Custom exceptions for the embedder module.
"""


class EmbedderError(Exception):
    """Base exception for embedder module."""
    pass


class ConfigurationError(EmbedderError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(EmbedderError):
    """Raised when input data validation fails."""
    pass


class EmbeddingError(EmbedderError):
    """Raised when embedding generation fails."""
    pass


class DatabaseError(EmbedderError):
    """Raised when database operations fail."""
    pass


class RetryExhaustedError(EmbedderError):
    """Raised when all retry attempts are exhausted."""
    pass