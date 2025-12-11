"""
Configuration management module.
"""

from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """Configuration manager for URL scraper."""
    
    def __init__(self, config_data: Dict[str, Any]):
        """
        Initialize configuration.
        
        Args:
            config_data: Configuration dictionary from YAML.
            
        Raises:
            ConfigurationError: If required fields are missing.
        """
        self._validate(config_data)
        self._config = config_data
    
    @classmethod
    def load(cls, config_path: str) -> "Config":
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config.yaml file.
            
        Returns:
            Config instance.
            
        Raises:
            ConfigurationError: If file is missing or invalid.
        """
        path = Path(config_path)
        if not path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}"
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            return cls(config_data)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in config file: {e}"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Error loading config file: {e}"
            )
    
    def _validate(self, config_data: Dict[str, Any]) -> None:
        """
        Validate configuration structure.
        
        Args:
            config_data: Configuration dictionary.
            
        Raises:
            ConfigurationError: If required fields are missing.
        """
        required_keys = [
            ("tech-trend-analysis", "analysis-report"),
            ("scrape", "url-scraped-content"),
            ("scrape", "timeout"),
            ("scrape", "log")
        ]
        
        for keys in required_keys:
            data = config_data
            path = []
            for key in keys:
                path.append(key)
                if key not in data:
                    raise ConfigurationError(
                        f"Missing required config: {'.'.join(path)}"
                    )
                data = data[key]
    
    @property
    def analysis_report_dir(self) -> str:
        """Get analysis report base directory."""
        return self._config["tech-trend-analysis"]["analysis-report"]
    
    @property
    def scraped_content_dir(self) -> str:
        """Get scraped content base directory."""
        return self._config["scrape"]["url-scraped-content"]
    
    @property
    def timeout(self) -> int:
        """Get request timeout in seconds."""
        return self._config["scrape"]["timeout"]
    
    @property
    def scrape_log_dir(self) -> str:
        """Get log directory."""
        return self._config["scrape"]["log"]
