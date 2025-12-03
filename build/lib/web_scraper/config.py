# src/web_scraper/config.py
"""Configuration management for web scraper."""

from pathlib import Path
from typing import Any, Dict
import yaml

from .exceptions import ConfigurationError


class Config:
    """Configuration loader and validator."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file
            
        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load()
        self._validate()
    
    def _load(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}"
            )
        
        try:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config: {e}")
    
    def _validate(self) -> None:
        """Validate required configuration keys."""
        required_keys = {
            'tech-trend-analysis': ['analysis-report'],
            'scrape': ['url-scraped-content', 'timeout', 'log', 'max-search-results']
        }
        
        for section, keys in required_keys.items():
            if section not in self._config:
                raise ConfigurationError(f"Missing config section: {section}")
            
            for key in keys:
                if key not in self._config[section]:
                    raise ConfigurationError(
                        f"Missing config key: {section}.{key}"
                    )
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            path: Configuration path (e.g., 'scrape.timeout')
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        keys = path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value