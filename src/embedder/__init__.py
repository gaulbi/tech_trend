"""
Embedder package for RAG pipeline.
Chunk articles, embed text, and store in ChromaDB.
"""

from .config import load_config
from .processor import EmbeddingProcessor

__version__ = "1.0.0"
__all__ = ["load_config", "EmbeddingProcessor"]