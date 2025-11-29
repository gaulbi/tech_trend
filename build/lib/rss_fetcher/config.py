"""Configuration management for RSS Fetcher."""

from pathlib import Path
from typing import Dict, Any
import yaml


class Config:
    """Manages application configuration from YAML file."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to configuration YAML file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config or {}
    
    def _validate_config(self) -> None:
        """Validate required configuration keys."""
        if 'rss' not in self._config:
            raise ValueError("Missing 'rss' section in config")
        
        rss_config = self._config['rss']
        required_keys = ['rss-list', 'rss-feed']
        
        for key in required_keys:
            if key not in rss_config:
                raise ValueError(f"Missing required config key: rss.{key}")
    
    @property
    def rss_list_path(self) -> Path:
        """Get path to RSS sources JSON file."""
        return Path(self._config['rss']['rss-list'])
    
    @property
    def rss_feed_dir(self) -> Path:
        """Get base directory for RSS feed output."""
        return Path(self._config['rss']['rss-feed'])
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value