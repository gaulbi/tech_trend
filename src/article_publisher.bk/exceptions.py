# ==============================================================================
# FILE: src/article_publisher/exceptions.py
# ==============================================================================
"""Custom exceptions for article publisher."""


class ArticlePublisherError(Exception):
    """Base exception for article publisher."""
    pass


class ConfigurationError(ArticlePublisherError):
    """Raised when configuration is invalid or missing."""
    pass


class PublishError(ArticlePublisherError):
    """Raised when article publishing fails."""
    pass