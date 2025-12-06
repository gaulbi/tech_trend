# ==============================================================================
# FILE: src/article_publisher/config.py
# ==============================================================================
"""Configuration management."""

import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml

from .exceptions import ConfigurationError
from .timezone_utils import validate_timezone


def load_config(config_path: str = "./config.yaml") -> Dict[str, Any]:
    """
    Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict containing validated configuration
        
    Raises:
        ConfigurationError: If config is missing or invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}"
        )
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    
    # Validate required sections
    if 'article-publisher' not in config:
        raise ConfigurationError(
            "Missing 'article-publisher' section in config"
        )
    
    pub_config = config['article-publisher']
    
    # Validate required fields
    if 'publication-id' not in pub_config:
        raise ConfigurationError(
            "Missing 'article-publisher.publication-id' in config"
        )
    
    # Validate publication-id format (should be non-empty alphanumeric)
    pub_id = pub_config['publication-id']
    if not pub_id or not isinstance(pub_id, str) or not pub_id.strip():
        raise ConfigurationError(
            "Invalid 'article-publisher.publication-id': "
            "must be non-empty string"
        )
    
    # Validate publication-id looks like a hash (alphanumeric)
    if not re.match(r'^[a-zA-Z0-9]+$', pub_id):
        raise ConfigurationError(
            f"Invalid 'article-publisher.publication-id' format: {pub_id}"
        )
    
    # Set defaults
    pub_config.setdefault('timeout', 60)
    pub_config.setdefault('retry', 3)
    pub_config.setdefault('log', 'log/article-publisher')
    pub_config.setdefault('api-header', 'X-Hashnode-Api-Key')
    pub_config.setdefault('server', 'https://gql.hashnode.com')
    pub_config.setdefault('timezone', 'America/New_York')
    pub_config.setdefault('rate-limit-delay', 1.0)
    
    # Validate timezone
    validate_timezone(pub_config['timezone'])
    
    if 'article-generator' not in config:
        config['article-generator'] = {}
    
    config['article-generator'].setdefault(
        'tech-trend-article',
        'data/tech-trend-article'
    )
    
    return config


def get_api_key() -> str:
    """
    Get Hashnode API key from environment.
    
    Returns:
        API key string
        
    Raises:
        ConfigurationError: If API key not found
    """
    api_key = os.getenv('HASHNODE_API_KEY')
    if not api_key:
        raise ConfigurationError(
            "HASHNODE_API_KEY environment variable not set. "
            "Please set it in .env file or environment."
        )
    return api_key