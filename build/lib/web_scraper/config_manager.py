"""
Configuration Manager Module

Handles loading and validating configuration from YAML files and environment variables.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class ConfigManager:
    """
    Manages application configuration from YAML files and environment variables.
    
    Loads settings from config.yaml and API keys from .env file.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        
        # Load environment variables from .env
        load_dotenv()
        logger.info("Loaded environment variables from .env file")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        if not self.config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from {self.config_path}")
            self._validate_config()
            self._load_api_keys()
            
            return self._config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {str(e)}")
    
    def _validate_config(self) -> None:
        """
        Validate required configuration keys are present.
        
        Raises:
            ConfigurationError: If required keys are missing
        """
        required_keys = {
            'tech-trend-analysis': ['analysis-report'],
            'llm': ['server', 'llm-model'],
            'scrap': ['url-scrapped-content', 'timeout']
        }
        
        for section, keys in required_keys.items():
            if section not in self._config:
                raise ConfigurationError(f"Missing required section: {section}")
            
            for key in keys:
                if key not in self._config[section]:
                    raise ConfigurationError(
                        f"Missing required key '{key}' in section '{section}'"
                    )
        
        logger.info("Configuration validation passed")
    
    def _load_api_keys(self) -> None:
        """
        Load API keys from environment variables.
        
        Raises:
            ConfigurationError: If required API keys are missing
        """
        api_keys = {
            'SCRAPERAPI_KEY': os.getenv('SCRAPERAPI_KEY'),
            'SCRAPINGBEE_KEY': os.getenv('SCRAPINGBEE_KEY'),
            'ZENROWS_KEY': os.getenv('ZENROWS_KEY')
        }
        
        # At least one API key must be present
        valid_keys = {k: v for k, v in api_keys.items() if v}
        
        if not valid_keys:
            raise ConfigurationError(
                "No valid scraper API keys found in environment. "
                "Please set at least one of: SCRAPERAPI_KEY, SCRAPINGBEE_KEY, ZENROWS_KEY"
            )
        
        self._config['api_keys'] = valid_keys
        logger.info(f"Loaded {len(valid_keys)} API key(s): {', '.join(valid_keys.keys())}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., 'scrap.timeout')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        return self._config