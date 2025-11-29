"""
Configuration Manager Module

Handles loading and validating configuration from YAML files.
"""

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages application configuration loaded from YAML file.
    
    Attributes:
        config_path: Path to the configuration file
        config: Dictionary containing all configuration settings
    """
    
    def __init__(self, config_path: str):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If required configuration keys are missing
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
        logger.info(f"Configuration loaded from {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
    
    def _validate_config(self) -> None:
        """
        Validate that all required configuration keys exist.
        
        Raises:
            ValueError: If required keys are missing
        """
        required_keys = [
            'tech-trend-analysis',
            'llm',
            'scrap'
        ]
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Validate nested keys
        if 'analysis-report' not in self.config['tech-trend-analysis']:
            raise ValueError("Missing 'analysis-report' in tech-trend-analysis config")
        
        if 'url-scrapped-content' not in self.config['scrap']:
            raise ValueError("Missing 'url-scrapped-content' in scrap config")
    
    @property
    def analysis_report_base_path(self) -> Path:
        """Get base path for tech trend analysis reports."""
        return Path(self.config['tech-trend-analysis']['analysis-report'])
    
    @property
    def url_scrapped_content_base_path(self) -> Path:
        """Get base path for scrapped content output."""
        return Path(self.config['scrap']['url-scrapped-content'])
    
    @property
    def scrap_timeout(self) -> int:
        """Get timeout for scraping operations."""
        return self.config['scrap'].get('timeout', 60)
    
    @property
    def llm_server(self) -> str:
        """Get LLM server name."""
        return self.config['llm'].get('server', 'openai')
    
    @property
    def llm_model(self) -> str:
        """Get LLM model name."""
        return self.config['llm'].get('llm-model', 'gpt-4')
    
    @property
    def llm_timeout(self) -> int:
        """Get LLM API timeout."""
        return self.config['llm'].get('timeout', 60)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value