"""RSS Fetcher package."""

__version__ = "1.0.0"

from .config import Config, ConfigurationError
from .validator import ValidationError

__all__ = [
    'Config',
    'ConfigurationError',
    'ValidationError',
]