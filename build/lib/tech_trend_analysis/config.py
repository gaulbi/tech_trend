"""Configuration management for tech trend analysis."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError


@dataclass
class RSSConfig:
    """RSS feed configuration."""
    rss_feed: Path


@dataclass
class TechTrendConfig:
    """Tech trend analysis configuration."""
    prompt: Path
    analysis_report: Path


@dataclass
class LLMConfig:
    """LLM configuration."""
    server: str
    llm_model: str
    timeout: int
    retry: int


@dataclass
class Config:
    """Main configuration container."""
    rss: RSSConfig
    tech_trend_analysis: TechTrendConfig
    llm: LLMConfig


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Config object with all settings

    Raises:
        ConfigurationError: If config file is missing or invalid
    """
    load_dotenv()
    
    path = Path(config_path)
    if not path.exists():
        raise ConfigurationError(f"Config file not found: {config_path}")
    
    try:
        with open(path, 'r') as f:
            data: Dict[str, Any] = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    
    try:
        rss_config = RSSConfig(
            rss_feed=Path(data['rss']['rss-feed'])
        )
        
        tech_config = TechTrendConfig(
            prompt=Path(data['tech-trend-analysis']['prompt']),
            analysis_report=Path(data['tech-trend-analysis']['analysis-report'])
        )
        
        llm_config = LLMConfig(
            server=data['llm']['server'],
            llm_model=data['llm']['llm-model'],
            timeout=data['llm']['timeout'],
            retry=data['llm']['retry']
        )
        
        return Config(rss=rss_config, tech_trend_analysis=tech_config, 
                      llm=llm_config)
    except KeyError as e:
        raise ConfigurationError(f"Missing required config key: {e}")