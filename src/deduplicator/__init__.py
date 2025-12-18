"""
Semantic deduplication package for tech trends.
"""
from .core import DeduplicationPipeline, Deduplicator
from .config import Config, load_config
from .exceptions import (
    DeduplicationError,
    ConfigurationError,
    ValidationError,
    EmbeddingError,
    DatabaseError,
)

__version__ = "1.0.0"

__all__ = [
    "DeduplicationPipeline",
    "Deduplicator",
    "Config",
    "load_config",
    "DeduplicationError",
    "ConfigurationError",
    "ValidationError",
    "EmbeddingError",
    "DatabaseError",
]
