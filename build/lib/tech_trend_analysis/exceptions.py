"""Custom exception classes for tech trend analysis."""


class TechTrendAnalysisError(Exception):
    """Base exception for all tech trend analysis errors."""
    pass


class ConfigurationError(TechTrendAnalysisError):
    """Raised when configuration is missing or invalid."""
    pass


class ValidationError(TechTrendAnalysisError):
    """Raised when data validation fails."""
    pass


class LLMError(TechTrendAnalysisError):
    """Raised when LLM API calls fail."""
    pass


class NetworkError(TechTrendAnalysisError):
    """Raised when network operations fail."""
    pass