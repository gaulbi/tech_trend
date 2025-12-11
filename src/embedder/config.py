"""
Configuration loader and validator.
"""

from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
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
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error reading config file: {e}")
    
    # Validate required sections
    required_sections = ['scrape', 'embedding']
    for section in required_sections:
        if section not in config:
            raise ConfigurationError(f"Missing required section: {section}")
    
    # Validate scrape section
    if 'url-scraped-content' not in config['scrape']:
        raise ConfigurationError(
            "Missing 'url-scraped-content' in scrape section"
        )
    
    # Validate embedding section
    required_embedding_keys = [
        'chunk-size',
        'chunk-overlap',
        'embedding-provider',
        'embedding-model',
        'database-path',
    ]
    
    for key in required_embedding_keys:
        if key not in config['embedding']:
            raise ConfigurationError(
                f"Missing '{key}' in embedding section"
            )
    
    # Set defaults for optional values
    config['embedding'].setdefault('timeout', 60)
    config['embedding'].setdefault('max-retries', 3)
    config['embedding'].setdefault('batch-size', 50)
    config['embedding'].setdefault('ktop', 20)
    config['embedding'].setdefault('log', 'log/embedding')
    
    # Load environment variables
    load_dotenv()
    
    return config


def get_scrape_path(config: Dict[str, Any], feed_date: str) -> Path:
    """
    Get the base path for scraped content.
    
    Args:
        config: Configuration dictionary
        feed_date: Feed date in YYYY-MM-DD format
        
    Returns:
        Path to scraped content directory
    """
    base_path = Path(config['scrape']['url-scraped-content'])
    return base_path / feed_date


def get_database_path(config: Dict[str, Any]) -> Path:
    """
    Get the path for ChromaDB database.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Path to database directory
    """
    return Path(config['embedding']['database-path'])

def get_collection_name(config: Dict[str, Any]) -> str:
    """
    Get the ChromaDB collection name

    Args:
        config: Configuration dictionary
    
    Returns:
        collection name
    """
    return config['embedding']['collection-name']