# src/web_scraper/config.py
"""Configuration management for web scraper."""

import os
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError


class Config:
    """Configuration loader and validator."""
    
    CONFIG_FILE = "config.yaml"
    
    def __init__(self) -> None:
        """Initialize configuration from config.yaml and .env files."""
        self._load_env()
        self._config = self._load_yaml()
        self._validate()
    
    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        load_dotenv()
    
    def _load_yaml(self) -> Dict[str, Any]:
        """
        Load and parse YAML configuration file.
        
        Returns:
            Dict[str, Any]: Parsed configuration
            
        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        config_path = Path(self.CONFIG_FILE)
        
        if not config_path.exists():
            raise ConfigurationError(
                f"Configuration file '{self.CONFIG_FILE}' not found"
            )
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
    
    def _validate(self) -> None:
        """
        Validate required configuration keys.
        
        Raises:
            ConfigurationError: If required keys are missing
        """
        required_keys = [
            'tech-trend-analysis',
            'scrap'
        ]
        
        for key in required_keys:
            if key not in self._config:
                raise ConfigurationError(
                    f"Missing required config key: {key}"
                )
        
        if 'analysis-report' not in self._config['tech-trend-analysis']:
            raise ConfigurationError(
                "Missing 'analysis-report' in tech-trend-analysis config"
            )
        
        if 'url-scrapped-content' not in self._config['scrap']:
            raise ConfigurationError(
                "Missing 'url-scrapped-content' in scrap config"
            )
    
    @property
    def analysis_report_dir(self) -> str:
        """Get analysis report directory path."""
        return self._config['tech-trend-analysis']['analysis-report']
    
    @property
    def scrapped_content_dir(self) -> str:
        """Get scrapped content directory path."""
        return self._config['scrap']['url-scrapped-content']
    
    @property
    def timeout(self) -> int:
        """Get HTTP timeout in seconds."""
        return self._config['scrap'].get('timeout', 60)
    
    @property
    def scraperapi_key(self) -> str:
        """Get ScraperAPI key from environment."""
        return os.getenv('SCRAPERAPI_KEY', '')
    
    @property
    def scrapingbee_key(self) -> str:
        """Get ScrapingBee key from environment."""
        return os.getenv('SCRAPINGBEE_KEY', '')
    
    @property
    def zenrows_key(self) -> str:
        """Get ZenRows key from environment."""
        return os.getenv('ZENROWS_KEY', '')
    
    @property
    def log_dir(self) -> str:
        """Get log directory path for web scraper logs."""
        return self._config['scrap'].get('log', 'log/scrapped')