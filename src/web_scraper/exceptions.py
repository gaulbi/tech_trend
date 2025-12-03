# src/web_scraper/exceptions.py
"""Custom exceptions for the web scraper module."""


class WebScraperError(Exception):
    """Base exception for web scraper errors."""
    pass


class ConfigurationError(WebScraperError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(WebScraperError):
    """Raised when input data validation fails."""
    pass


class ScraperAPIError(WebScraperError):
    """Raised when scraper API requests fail."""
    pass