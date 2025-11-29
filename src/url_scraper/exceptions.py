"""Custom exceptions for URL scraper."""


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""
    pass


class ValidationError(Exception):
    """Raised when input data validation fails."""
    pass