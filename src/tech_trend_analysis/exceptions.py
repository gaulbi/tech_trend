# ============================================================================
# src/tech_trend_analysis/exceptions.py
# ============================================================================

"""Custom exceptions for the tech trend analysis module."""


class TechTrendAnalysisError(Exception):
    """Base exception for tech trend analysis errors."""
    pass


class ConfigurationError(TechTrendAnalysisError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(TechTrendAnalysisError):
    """Raised when data validation fails."""
    pass


class LLMError(TechTrendAnalysisError):
    """Raised when LLM operations fail."""
    pass
