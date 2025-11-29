"""
Article Generator Package

Production-grade article generation using LLMs and ChromaDB.
"""

__version__ = "1.0.0"
__author__ = "Article Generator Team"

from src.article_generator.config_loader import ConfigLoader, Config
from src.article_generator.article_service import ArticleService
from src.article_generator.chromadb_service import ChromaDBService
from src.article_generator.prompt_service import PromptService
from src.article_generator.llm_client_base import LLMClientBase, LLMClientFactory
from src.article_generator.embedding_client_base import EmbeddingClientBase, EmbeddingClientFactory
from src.article_generator.report_generator import ReportGenerator
from src.article_generator.schema_validator import SchemaValidator

__all__ = [
    'ConfigLoader',
    'Config',
    'ArticleService',
    'ChromaDBService',
    'PromptService',
    'LLMClientBase',
    'LLMClientFactory',
    'EmbeddingClientBase',
    'EmbeddingClientFactory',
    'ReportGenerator',
    'SchemaValidator'
]