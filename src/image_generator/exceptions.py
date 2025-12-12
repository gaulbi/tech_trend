"""
Custom exceptions for the image generator module.
"""


class ImageGeneratorError(Exception):
    """Base exception for image generator errors."""
    pass


class ConfigurationError(ImageGeneratorError):
    """Raised when configuration is missing or invalid."""
    pass


class ValidationError(ImageGeneratorError):
    """Raised when input validation fails."""
    pass


class NetworkError(ImageGeneratorError):
    """Raised when network operations fail."""
    pass


class LLMProviderError(ImageGeneratorError):
    """Raised when LLM provider operations fail."""
    pass
