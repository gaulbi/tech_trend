"""
Custom exceptions for wiki_search module.
"""


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(Exception):
    """Raised when input data validation fails."""
    pass