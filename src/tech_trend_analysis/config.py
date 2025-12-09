# ============================================================================
# src/tech_trend_analysis/config.py
# ============================================================================

"""Configuration management for tech trend analysis."""

import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError


class Config:
    """Manages application configuration."""

    def __init__(self, config_path: str = "./config.yaml"):
        """
        Initialize configuration.

        Args:
            config_path: Path to the configuration file

        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
        self._load_env()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}"
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in config file: {e}"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load config file: {e}"
            )

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        load_dotenv()

    @property
    def rss_feed_path(self) -> str:
        """Get RSS feed base path."""
        return self._config.get('rss', {}).get('rss-feed', 'data/rss/rss-feed')

    @property
    def prompt_path(self) -> str:
        """Get prompt template path."""
        return self._config.get(
            'tech-trend-analysis', {}
        ).get('prompt', 'prompt/tech-trend-analysis-prompt.md')

    @property
    def analysis_report_path(self) -> str:
        """Get analysis report base path."""
        return self._config.get(
            'tech-trend-analysis', {}
        ).get('analysis-report', 'data/tech-trend-analysis')

    @property
    def log_path(self) -> str:
        """Get log file base path."""
        return self._config.get(
            'tech-trend-analysis', {}
        ).get('log', 'log/tech-trend-analysis')

    @property
    def llm_server(self) -> str:
        """Get LLM server type."""
        return self._config.get('llm', {}).get('server', 'openai')

    @property
    def llm_model(self) -> str:
        """Get LLM model name."""
        return self._config.get('llm', {}).get('llm-model', 'gpt-4')

    @property
    def llm_timeout(self) -> int:
        """Get LLM request timeout in seconds."""
        return self._config.get('llm', {}).get('timeout', 60)

    @property
    def llm_retry(self) -> int:
        """Get number of retry attempts for LLM requests."""
        return self._config.get('llm', {}).get('retry', 3)

    def get_api_key(self, provider: str) -> str:
        """
        Get API key for the specified provider.

        Args:
            provider: LLM provider name (openai, deepseek, claude)

        Returns:
            API key from environment variables

        Raises:
            ConfigurationError: If API key is not found
        """
        key_map = {
            'openai': 'OPENAI_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
            'claude': 'CLAUDE_API_KEY',
        }

        env_var = key_map.get(provider.lower())
        if not env_var:
            raise ConfigurationError(f"Unknown provider: {provider}")

        api_key = os.getenv(env_var)
        if not api_key and provider.lower() != 'ollama':
            raise ConfigurationError(
                f"API key not found for {provider}. "
                f"Set {env_var} in .env file"
            )

        return api_key or ""