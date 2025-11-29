"""Configuration management for URL scraper."""

from pathlib import Path
from typing import Dict, Any
import yaml

from .exceptions import ConfigurationError


class Config:
    """Configuration loader and validator."""
    
    def __init__(self, config_path: Path = Path("config.yaml")):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            dict: Parsed configuration
            
        Raises:
            ConfigurationError: If file is missing or invalid YAML
        """
        if not self.config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}"
            )
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
    
    def _validate_config(self) -> None:
        """
        Validate required configuration keys exist.
        
        Raises:
            ConfigurationError: If required keys are missing
        """
        required_keys = [
            ("tech-trend-analysis", "analysis-report"),
            ("scrape", "url-scraped-content"),
            ("scrape", "timeout"),
            ("scrape", "log")
        ]
        
        for *parents, key in required_keys:
            current = self.config
            path = []
            
            for parent in parents:
                if parent not in current:
                    raise ConfigurationError(
                        f"Missing config key: {'.'.join([*path, parent])}"
                    )
                current = current[parent]
                path.append(parent)
            
            if key not in current:
                raise ConfigurationError(
                    f"Missing config key: {'.'.join([*path, key])}"
                )
    
    @property
    def analysis_report_dir(self) -> Path:
        """Get tech trend analysis base directory."""
        return Path(self.config["tech-trend-analysis"]["analysis-report"])
    
    @property
    def scrapped_content_dir(self) -> Path:
        """Get scraped content base directory."""
        return Path(self.config["scrape"]["url-scraped-content"])
    
    @property
    def timeout(self) -> int:
        """Get request timeout in seconds."""
        return int(self.config["scrape"]["timeout"])
    
    @property
    def log_dir(self) -> Path:
        """Get log directory."""
        return Path(self.config["scrape"]["log"])