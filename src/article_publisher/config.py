"""Configuration management for article publisher."""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

import yaml

from .exceptions import ConfigurationError


def load_config(config_path: str = "./config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigurationError: If config file is missing or invalid
    """
    load_dotenv()
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}"
        )
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML configuration: {e}")
    
    # Validate required sections
    required_sections = [
        "article-publisher",
        "article-generator",
        "image-generator"
    ]
    
    for section in required_sections:
        if section not in config:
            raise ConfigurationError(
                f"Missing required section: {section}"
            )
    
    # Validate article-publisher section
    required_fields = [
        "timeout",
        "retry",
        "log",
        "api-header",
        "server",
        "publication-id",
        "timezone",
        "published-article"
    ]
    
    for field in required_fields:
        if field not in config["article-publisher"]:
            raise ConfigurationError(
                f"Missing required field: article-publisher.{field}"
            )
    
    # Validate API key
    api_key = os.getenv("HASHNODE_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "HASHNODE_API_KEY environment variable not set"
        )
    
    return config


def get_api_key() -> str:
    """
    Get Hashnode API key from environment.
    
    Returns:
        API key string
        
    Raises:
        ConfigurationError: If API key is not set
    """
    api_key = os.getenv("HASHNODE_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "HASHNODE_API_KEY environment variable not set"
        )
    return api_key
