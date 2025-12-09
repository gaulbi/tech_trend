"""
Custom exceptions for wiki_search module.
"""


class WikiSearchError(Exception):
    """Base exception for wiki_search module."""
    pass


class ConfigurationError(WikiSearchError):
    """Raised when configuration is missing or invalid."""
    pass


class ValidationError(WikiSearchError):
    """Raised when input data validation fails."""
    pass