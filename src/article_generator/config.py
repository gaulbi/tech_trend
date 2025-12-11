# ============================================================================
# src/article_generator/config.py
# ============================================================================
"""Configuration management."""
import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv
from .exceptions import ConfigurationError


class Config:
    """Configuration manager."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file
            
        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        load_dotenv()
        
        if not Path(config_path).exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config: Dict[str, Any] = yaml.safe_load(f)
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration structure."""
        required_keys = [
            'llm', 'tech-trend-analysis', 'article-generator',
            'embedding', 'rag'
        ]
        for key in required_keys:
            if key not in self._config:
                raise ConfigurationError(f"Missing required config: {key}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get config value by dot-notation path.
        
        Args:
            key_path: Dot-separated path (e.g., 'llm.server')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_api_key(self, provider: str) -> str:
        """
        Get API key from environment.
        
        Args:
            provider: Provider name (openai, deepseek, etc.)
            
        Returns:
            API key
            
        Raises:
            ConfigurationError: If API key not found
        """
        key_map = {
            'openai': 'OPENAI_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
            'claude': 'CLAUDE_API_KEY',
            'voyageai': 'VOYAGEAI_API_KEY',
            'gemini': 'GEMINI_API_KEY'
        }
        
        env_var = key_map.get(provider.lower())
        if not env_var:
            raise ConfigurationError(f"Unknown provider: {provider}")
        
        api_key = os.getenv(env_var)
        if not api_key:
            raise ConfigurationError(
                f"API key not found: {env_var}"
            )
        
        return api_key