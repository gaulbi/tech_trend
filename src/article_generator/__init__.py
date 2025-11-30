"""Article generator package."""

from .config import Config, ConfigurationError, load_config
from .factories import (
    BaseEmbeddingClient,
    BaseLLMClient,
    EmbeddingFactory,
    LLMFactory,
)
from .rag_engine import RAGEngine
from .utils import (
    JSONFormatter,
    ensure_directory,
    get_today_date,
    inject_prompt_variables,
    load_prompt_template,
    setup_logger,
    slugify,
)

__all__ = [
    "Config",
    "ConfigurationError",
    "load_config",
    "BaseLLMClient",
    "BaseEmbeddingClient",
    "LLMFactory",
    "EmbeddingFactory",
    "RAGEngine",
    "get_today_date",
    "slugify",
    "setup_logger",
    "JSONFormatter",
    "load_prompt_template",
    "inject_prompt_variables",
    "ensure_directory",
]