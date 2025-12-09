"""
Configuration management for wiki_search module.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml

from .exceptions import ConfigurationError

CONFIG_FILE = "config.yaml"


class Config:
    """Manages application configuration from YAML file."""

    def __init__(self, config_path: str = CONFIG_FILE) -> None:
        """
        Initialize configuration.

        Args:
            config_path: Path to config.yaml file

        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration file.

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        if not self.config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}"
            )

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in config file: {e}"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Error reading config file: {e}"
            )

        if config is None:
            raise ConfigurationError("Config file is empty")

        self._validate_config(config)
        return config

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate required configuration keys and types.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ConfigurationError: If required keys are missing or invalid
        """
        required_keys = [
            ("tech-trend-analysis", "analysis-report"),
            ("scrape", "url-scraped-content"),
            ("scrape", "log"),
            ("scrape", "max-search-results"),
        ]

        for *sections, key in required_keys:
            current = config
            path = []
            for section in sections:
                path.append(section)
                if section not in current:
                    raise ConfigurationError(
                        f"Missing config section: {'.'.join(path)}"
                    )
                current = current[section]

            if key not in current:
                path.append(key)
                raise ConfigurationError(
                    f"Missing config key: {'.'.join(path)}"
                )

        # Validate max-search-results is a positive integer
        try:
            max_results = int(config["scrape"]["max-search-results"])
            if max_results <= 0:
                raise ConfigurationError(
                    "scrape.max-search-results must be a positive integer"
                )
        except (ValueError, TypeError):
            raise ConfigurationError(
                "scrape.max-search-results must be a valid integer"
            )

    @property
    def analysis_report_base(self) -> str:
        """Get base path for tech trend analysis reports."""
        return self._config["tech-trend-analysis"]["analysis-report"]

    @property
    def scraped_content_base(self) -> str:
        """Get base path for scraped content output."""
        return self._config["scrape"]["url-scraped-content"]

    @property
    def log_dir(self) -> str:
        """Get log directory path."""
        return self._config["scrape"]["log"]

    @property
    def max_search_results(self) -> int:
        """Get maximum number of search results per query."""
        return int(self._config["scrape"]["max-search-results"])