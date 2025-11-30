"""Configuration loader and validator for the embedder module."""

from pathlib import Path
from typing import Any, Dict

import yaml

from .exceptions import ConfigurationError


class Config:
    """Configuration container with validation."""

    def __init__(self, config_dict: Dict[str, Any]) -> None:
        """
        Initialize configuration.

        Args:
            config_dict: Raw configuration dictionary from YAML.

        Raises:
            ConfigurationError: If required fields are missing.
        """
        self._validate(config_dict)
        self._config = config_dict

    def _validate(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration structure.

        Args:
            config: Configuration dictionary to validate.

        Raises:
            ConfigurationError: If validation fails.
        """
        required_sections = ["scrape", "embedding"]
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(
                    f"Missing required section: {section}"
                )

        # Validate scrape section
        if "url-scraped-content" not in config["scrape"]:
            raise ConfigurationError(
                "Missing 'url-scraped-content' in scrape section"
            )

        # Validate embedding section
        required_embedding = [
            "chunk-size",
            "chunk-overlap",
            "embedding-provider",
            "embedding-model",
            "database-path",
        ]
        for field in required_embedding:
            if field not in config["embedding"]:
                raise ConfigurationError(
                    f"Missing '{field}' in embedding section"
                )

    @property
    def scraped_content_path(self) -> str:
        """Get path to scraped content directory."""
        return self._config["scrape"]["url-scraped-content"]

    @property
    def chunk_size(self) -> int:
        """Get chunk size for text splitting."""
        return self._config["embedding"]["chunk-size"]

    @property
    def chunk_overlap(self) -> int:
        """Get chunk overlap size."""
        return self._config["embedding"]["chunk-overlap"]

    @property
    def embedding_provider(self) -> str:
        """Get embedding provider name."""
        return self._config["embedding"]["embedding-provider"]

    @property
    def embedding_model(self) -> str:
        """Get embedding model name."""
        return self._config["embedding"]["embedding-model"]

    @property
    def timeout(self) -> int:
        """Get API timeout in seconds."""
        return self._config["embedding"].get("timeout", 60)

    @property
    def max_retries(self) -> int:
        """Get maximum number of retries."""
        return self._config["embedding"].get("max-retries", 3)

    @property
    def batch_size(self) -> int:
        """Get batch size for embedding API calls."""
        return self._config["embedding"].get("batch-size", 50)

    @property
    def database_path(self) -> str:
        """Get path to ChromaDB database."""
        return self._config["embedding"]["database-path"]

    @property
    def ktop(self) -> int:
        """Get number of top results to return."""
        return self._config["embedding"].get("ktop", 20)

    @property
    def log_path(self) -> str:
        """Get path to log directory."""
        return self._config["embedding"].get("log", "log/embedding")

    @property
    def collection_name(self) -> str:
        """Get collection name for embeddings."""
        return self._config["embedding"].get("collection-name", "tech_trends")


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load and validate configuration from YAML file.

    Args:
        config_path: Path to configuration file.

    Returns:
        Validated Config object.

    Raises:
        ConfigurationError: If file doesn't exist or is invalid.
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}"
        )

    try:
        with open(config_file, "r") as f:
            config_dict = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(
            f"Invalid YAML in configuration file: {e}"
        ) from e

    if not config_dict:
        raise ConfigurationError("Configuration file is empty")

    return Config(config_dict)