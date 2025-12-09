"""
Wikipedia Search Package

A production-grade module for searching Wikipedia based on tech trend keywords,
extracting content, cleaning it, and storing results.
"""

__version__ = "1.0.0"
__author__ = "Tech Trend Analysis Team"

from .exceptions import ConfigurationError, ValidationError

__all__ = ["ConfigurationError", "ValidationError"]