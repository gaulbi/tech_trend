"""RSS Fetcher - Fetch and organize RSS feeds by category."""

__version__ = "1.0.0"

from .main import main
from .models import (
    Config,
    Article,
    CategoryOutput,
    ConfigurationError,
    ValidationError
)

__all__ = [
    "main",
    "Config",
    "Article",
    "CategoryOutput",
    "ConfigurationError",
    "ValidationError",
]