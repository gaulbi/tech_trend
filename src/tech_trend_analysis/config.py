# ============================================================================
# FILE: src/tech_trend_analysis/config.py
# ============================================================================
"""Configuration management."""

from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml package is not installed.", file=sys.stderr)
    print("Please install it with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from .exceptions import ConfigurationError


class Config:
    """Configuration manager for tech trend analysis."""
    
    def __init__(self, config_path: Path):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to config.yaml
            
        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        if not config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path.absolute()}\n"
                f"Please create config.yaml in the project root directory."
            )
        
        try:
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate required configuration keys."""
        required_keys = ['rss', 'tech-trend-analysis', 'llm']
        for key in required_keys:
            if key not in self._config:
                raise ConfigurationError(
                    f"Missing required config section: {key}"
                )
    
    @property
    def rss_feed_path(self) -> str:
        """Get RSS feed base path."""
        return self._config['rss']['rss-feed']
    
    @property
    def prompt_path(self) -> str:
        """Get prompt template path."""
        return self._config['tech-trend-analysis']['prompt']
    
    @property
    def analysis_report_path(self) -> str:
        """Get analysis report base path."""
        return self._config['tech-trend-analysis']['analysis-report']
    
    @property
    def log_path(self) -> str:
        """Get log base path."""
        return self._config['tech-trend-analysis']['log']
    
    @property
    def llm_server(self) -> str:
        """Get LLM server type."""
        return self._config['llm']['server']
    
    @property
    def llm_model(self) -> str:
        """Get LLM model name."""
        return self._config['llm']['llm-model']
    
    @property
    def llm_timeout(self) -> int:
        """Get LLM request timeout."""
        return self._config['llm']['timeout']
    
    @property
    def llm_retry(self) -> int:
        """Get LLM retry count."""
        return self._config['llm']['retry']
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config.get(key, default)
