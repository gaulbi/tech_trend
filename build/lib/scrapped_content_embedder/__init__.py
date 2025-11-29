"""
Package initialization files for the scrapped_content_embedder package.
"""

# src/scrapped_content_embedder/__init__.py
"""
Scrapped Content Embedder Package

A production-grade module for embedding scraped web content into ChromaDB
using multiple embedding provider options.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .config import Config, ScrapConfig, EmbeddingConfig
from .embedding_clients import (
    EmbeddingClient,
    EmbeddingClientFactory,
    OpenAIEmbeddingClient,
    VoyageAIEmbeddingClient,
    GeminiEmbeddingClient,
    SentenceTransformerClient
)
from .embedder import ScrapedContentEmbedder

__all__ = [
    'Config',
    'ScrapConfig',
    'EmbeddingConfig',
    'EmbeddingClient',
    'EmbeddingClientFactory',
    'OpenAIEmbeddingClient',
    'VoyageAIEmbeddingClient',
    'GeminiEmbeddingClient',
    'SentenceTransformerClient',
    'ScrapedContentEmbedder'
]