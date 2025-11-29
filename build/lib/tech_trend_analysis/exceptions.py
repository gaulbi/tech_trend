"""Custom exceptions for tech trend analysis."""


class TechTrendAnalysisError(Exception):
    """Base exception for tech trend analysis."""
    pass


class ConfigurationError(TechTrendAnalysisError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(TechTrendAnalysisError):
    """Raised when data validation fails."""
    pass


class LLMProviderError(TechTrendAnalysisError):
    """Raised when LLM provider encounters an error."""
    pass