"""
Custom exception classes for the image generator.
"""


class ImageGeneratorError(Exception):
    """Base exception for image generator errors."""
    pass


class ConfigurationError(ImageGeneratorError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(ImageGeneratorError):
    """Raised when input validation fails."""
    pass


class NetworkError(ImageGeneratorError):
    """Raised when network operations fail."""
    pass


class HashNodeUploadError(ImageGeneratorError):
    """Raised when Hashnode upload fails."""
    pass


class LLMProviderError(ImageGeneratorError):
    """Raised when LLM provider operations fail."""
    pass
