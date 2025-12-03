"""
Configuration management for wiki_search module.
"""

from pathlib import Path
from typing import Any, Dict

import yaml

from .exceptions import ConfigurationError


def load_config(config_path: Path = Path("config.yaml")) -> Dict[str, Any]:
    """
    Load and validate configuration file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigurationError: If config file is missing or invalid
    """
    if not config_path.exists():
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise ConfigurationError(f"Failed to parse config.yaml: {e}")
    
    _validate_config(config)
    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validate required configuration keys exist.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ConfigurationError: If required keys are missing
    """
    required_keys = [
        'tech-trend-analysis.analysis-report',
        'scrape.url-scraped-content',
        'scrape.log'
    ]
    
    for key in required_keys:
        parts = key.split('.')
        current = config
        for part in parts:
            if part not in current:
                raise ConfigurationError(f"Missing config key: {key}")
            current = current[part]