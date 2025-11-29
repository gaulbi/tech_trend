"""Configuration loader for RSS fetcher."""

import yaml
from pathlib import Path
from typing import Dict
from .models import Config, ConfigurationError, ValidationError
import json


def load_config(config_path: str = "./config.yaml") -> Config:
    """
    Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml file
        
    Returns:
        Validated Config object
        
    Raises:
        ConfigurationError: If config file is missing or invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}"
        )
    
    try:
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        return Config(**config_data)
    except Exception as e:
        raise ConfigurationError(f"Invalid configuration: {str(e)}")


def load_rss_list(rss_list_path: str) -> Dict[str, Dict[str, str]]:
    """
    Load and validate RSS list from JSON file.
    
    Args:
        rss_list_path: Path to RSS list JSON file
        
    Returns:
        Dictionary mapping categories to feed sources
        
    Raises:
        ValidationError: If RSS list JSON is malformed
    """
    rss_file = Path(rss_list_path)
    
    if not rss_file.exists():
        raise ValidationError(
            f"RSS list file not found: {rss_list_path}"
        )
    
    try:
        with open(rss_file, 'r') as f:
            rss_data = json.load(f)
        
        if not isinstance(rss_data, dict):
            raise ValidationError("RSS list must be a JSON object")
        
        for category, feeds in rss_data.items():
            if not isinstance(feeds, dict):
                raise ValidationError(
                    f"Feeds for category '{category}' must be an object"
                )
        
        return rss_data
        
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in RSS list: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error loading RSS list: {str(e)}")