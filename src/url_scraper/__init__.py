"""
URL Scraper package.

This package provides functionality for scraping URLs from tech trend
analysis reports and extracting clean, readable content.
"""

from .config import Config, ConfigurationError
from .validator import ValidationError

__all__ = ["Config", "ConfigurationError", "ValidationError"]