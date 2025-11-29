"""Configuration management for tech trend analysis."""

import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError


class Config:
    """Configuration manager for tech trend analysis."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration.
        
        Args:
            config_path: Path to configuration YAML file
            
        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        self._config = self._load_config(config_path)
        self._load_env()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        if not os.path.exists(config_path):
            raise ConfigurationError(
                f"Configuration file not found: {config_path}"
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                raise ConfigurationError("Configuration file is empty")
            
            self._validate_config(config)
            return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration structure.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ConfigurationError: If required fields are missing
        """
        required_sections = ['rss', 'tech-trend-analysis', 'llm']
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(
                    f"Missing required section: {section}"
                )

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        load_dotenv()

    @property
    def rss_feed_path(self) -> str:
        """Get RSS feed base path."""
        return self._config['rss']['rss-feed']

    @property
    def prompt_path(self) -> str:
        """Get prompt template path."""
        return self._config['tech-trend-analysis']['prompt']

    @property
    def analysis_report_path(self) -> str:
        """Get analysis report base path."""
        return self._config['tech-trend-analysis']['analysis-report']

    @property
    def log_path(self) -> str:
        """Get log file base path."""
        return self._config['tech-trend-analysis']['log']

    @property
    def llm_server(self) -> str:
        """Get LLM server type."""
        return self._config['llm']['server']

    @property
    def llm_model(self) -> str:
        """Get LLM model name."""
        return self._config['llm']['llm-model']

    @property
    def llm_timeout(self) -> int:
        """Get LLM timeout in seconds."""
        return self._config['llm']['timeout']

    @property
    def llm_retry(self) -> int:
        """Get LLM retry count."""
        return self._config['llm']['retry']

    def get_api_key(self, provider: str) -> str:
        """Get API key for specified provider.
        
        Args:
            provider: Provider name (openai, deepseek, claude)
            
        Returns:
            API key from environment
            
        Raises:
            ConfigurationError: If API key is not set
        """
        key_map = {
            'openai': 'OPENAI_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
            'claude': 'CLAUDE_API_KEY'
        }
        
        env_var = key_map.get(provider.lower())
        if not env_var:
            return ""  # Ollama doesn't need API key
        
        api_key = os.getenv(env_var)
        if not api_key and provider.lower() != 'ollama':
            raise ConfigurationError(
                f"API key not found: {env_var}. "
                f"Please set it in .env file"
            )
        
        return api_key or ""