"""
Configuration management for the deduplication system.
"""
from pathlib import Path
from typing import Any, Dict
import yaml

from .exceptions import ConfigurationError


class Config:
    """Configuration container with typed access."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize configuration from dictionary."""
        self._data = data
        self._validate()
    
    def _validate(self) -> None:
        """Validate required configuration keys."""
        required_sections = ["deduplication", "tech-trend-analysis"]
        for section in required_sections:
            if section not in self._data:
                raise ConfigurationError(
                    f"Missing required section: {section}"
                )
        
        required_dedup_keys = [
            "history-keywords",
            "collection-name",
            "dedup-analysis-report",
            "similarity-threshold",
            "lookback-days",
            "target-count",
            "log",
            "embedding-provider",
            "embedding-model",
        ]
        
        for key in required_dedup_keys:
            if key not in self._data["deduplication"]:
                raise ConfigurationError(
                    f"Missing required key: deduplication.{key}"
                )
        
        required_analysis_keys = [
            "analysis-report",
            "org-analysis-report",
        ]
        
        for key in required_analysis_keys:
            if key not in self._data["tech-trend-analysis"]:
                raise ConfigurationError(
                    f"Missing required key: tech-trend-analysis.{key}"
                )
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path."""
        keys = path.split(".")
        value = self._data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @property
    def history_keywords_path(self) -> Path:
        """Get history keywords database path."""
        return Path(self.get("deduplication.history-keywords"))
    
    @property
    def collection_name(self) -> str:
        """Get ChromaDB collection name."""
        return self.get("deduplication.collection-name")
    
    @property
    def dedup_report_path(self) -> Path:
        """Get deduplicated analysis report base path."""
        return Path(self.get("deduplication.dedup-analysis-report"))
    
    @property
    def analysis_report_path(self) -> Path:
        """Get tech trend analysis report base path."""
        return Path(self.get("tech-trend-analysis.analysis-report"))
    
    @property
    def org_analysis_report_path(self) -> Path:
        """Get original tech trend analysis report base path."""
        return Path(self.get("tech-trend-analysis.org-analysis-report"))
    
    @property
    def similarity_threshold(self) -> float:
        """Get similarity threshold for duplicates."""
        return float(self.get("deduplication.similarity-threshold"))
    
    @property
    def lookback_days(self) -> int:
        """Get lookback period in days."""
        return int(self.get("deduplication.lookback-days"))
    
    @property
    def target_count(self) -> int:
        """Get target number of unique trends."""
        return int(self.get("deduplication.target-count"))
    
    @property
    def log_path(self) -> Path:
        """Get log directory path."""
        return Path(self.get("deduplication.log"))
    
    @property
    def embedding_provider(self) -> str:
        """Get embedding provider name."""
        return self.get("deduplication.embedding-provider")
    
    @property
    def embedding_model(self) -> str:
        """Get embedding model name."""
        return self.get("deduplication.embedding-model")
    
    @property
    def timeout(self) -> int:
        """Get API timeout in seconds."""
        return int(self.get("deduplication.timeout", 60))
    
    @property
    def max_retries(self) -> int:
        """Get maximum retry attempts."""
        return int(self.get("deduplication.max-retries", 3))


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Config object with validated configuration
        
    Raises:
        ConfigurationError: If config file is missing or invalid
    """
    path = Path(config_path)
    
    if not path.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}"
        )
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise ConfigurationError("Configuration file is empty")
        
        return Config(data)
        
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML format: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {e}")
