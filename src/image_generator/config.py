"""
Configuration management module.
"""
import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError


class ConfigManager:
    """Manages application configuration from YAML and environment variables."""
    
    CONFIG_FILE = "config.yaml"
    
    def __init__(self):
        """Initialize configuration manager."""
        load_dotenv()
        self._config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_path = Path(self.CONFIG_FILE)
        if not config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.CONFIG_FILE}"
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
    
    def _validate_config(self) -> None:
        """Validate required configuration sections exist."""
        required_sections = [
            'article-generator',
            'image-generator',
            'imgbb'
        ]
        
        for section in required_sections:
            if section not in self._config:
                raise ConfigurationError(
                    f"Missing required config section: {section}"
                )
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation path."""
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_env(self, key: str, required: bool = False) -> str:
        """Get environment variable value."""
        value = os.getenv(key)
        if required and not value:
            raise ConfigurationError(
                f"Required environment variable not set: {key}"
            )
        return value
    
    @property
    def article_base_path(self) -> Path:
        """Get base path for article input."""
        return Path(self.get('article-generator.tech-trend-article'))
    
    @property
    def image_output_path(self) -> Path:
        """Get base path for image output."""
        return Path(self.get('image-generator.image-path'))
    
    @property
    def thumbnail_output_path(self) -> Path:
        """Get base path for thumbnail image output."""
        return Path(self.get('image-generator.thumbnail-image-path'))
    
    @property
    def url_mapping_path(self) -> Path:
        """Get base path for URL mapping storage."""
        return Path(self.get('image-generator.url-mapping-path'))
    
    @property
    def log_path(self) -> Path:
        """Get path for log files."""
        return Path(self.get('image-generator.log'))
