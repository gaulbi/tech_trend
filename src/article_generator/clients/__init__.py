# ============================================================================
# src/article_generator/clients/__init__.py
# ============================================================================
"""Clients package for LLM and Embedding providers."""

from .base import BaseLLMClient, BaseEmbeddingClient
from .llm_clients import (
    OpenAIClient,
    DeepSeekClient,
    ClaudeClient,
    OllamaClient
)
from .embedding_clients import (
    OpenAIEmbedding,
    VoyageAIEmbedding,
    GeminiEmbedding,
    SentenceTransformersEmbedding
)
from .factories import LLMFactory, EmbeddingFactory

__all__ = [
    'BaseLLMClient',
    'BaseEmbeddingClient',
    'OpenAIClient',
    'DeepSeekClient',
    'ClaudeClient',
    'OllamaClient',
    'OpenAIEmbedding',
    'VoyageAIEmbedding',
    'GeminiEmbedding',
    'SentenceTransformersEmbedding',
    'LLMFactory',
    'EmbeddingFactory',
]