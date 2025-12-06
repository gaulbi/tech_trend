"""Configuration management for RSS fetcher."""

from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """Configuration loader and validator."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration.
        
        Args:
            config_path: Path to configuration file
            
        Raises:
            ConfigurationError: If config file missing or invalid
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If file doesn't exist or invalid YAML
        """
        if not self.config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}"
            )
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config is None:
                    raise ConfigurationError("Empty configuration file")
                return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML format: {e}")
    
    def _validate_config(self) -> None:
        """Validate required configuration keys exist.
        
        Raises:
            ConfigurationError: If required keys missing
        """
        if 'rss' not in self._config:
            raise ConfigurationError("Missing 'rss' section in config")
        
        required_keys = [
            'rss-source', 'rss-feed', 'log', 
            'max-concurrent', 'timeout', 'retry'
        ]
        
        missing = [
            k for k in required_keys 
            if k not in self._config['rss']
        ]
        
        if missing:
            raise ConfigurationError(
                f"Missing required config keys: {', '.join(missing)}"
            )
    
    @property
    def rss_source(self) -> str:
        """Get RSS source file path."""
        return self._config['rss']['rss-source']
    
    @property
    def rss_feed_dir(self) -> str:
        """Get RSS feed output directory."""
        return self._config['rss']['rss-feed']
    
    @property
    def log_dir(self) -> str:
        """Get log directory."""
        return self._config['rss']['log']
    
    @property
    def max_concurrent(self) -> int:
        """Get max concurrent requests."""
        return int(self._config['rss']['max-concurrent'])
    
    @property
    def timeout(self) -> int:
        """Get HTTP timeout in seconds."""
        return int(self._config['rss']['timeout'])
    
    @property
    def retry(self) -> int:
        """Get max retry attempts."""
        return int(self._config['rss']['retry'])