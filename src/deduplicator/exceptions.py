"""
Custom exceptions for the deduplication system.
"""


class DeduplicationError(Exception):
    """Base exception for deduplication errors."""
    pass


class ConfigurationError(DeduplicationError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(DeduplicationError):
    """Raised when input data validation fails."""
    pass


class EmbeddingError(DeduplicationError):
    """Raised when embedding generation fails."""
    pass


class DatabaseError(DeduplicationError):
    """Raised when database operations fail."""
    pass
