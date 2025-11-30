"""Configuration module for article generator."""

from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, Field, field_validator


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class LLMConfig(BaseModel):
    """LLM configuration settings."""
    
    server: str = Field(..., description="LLM provider name")
    llm_model: str = Field(..., alias="llm-model")
    timeout: int = Field(default=60, ge=1)
    retry: int = Field(default=3, ge=1)


class TechTrendAnalysisConfig(BaseModel):
    """Tech trend analysis paths."""
    
    analysis_report: str = Field(..., alias="analysis-report")


class ArticleGeneratorConfig(BaseModel):
    """Article generator settings."""
    
    system_prompt: str = Field(..., alias="system-prompt")
    user_prompt: str = Field(..., alias="user-prompt")
    tech_trend_article: str = Field(..., alias="tech-trend-article")
    log: str


class EmbeddingConfig(BaseModel):
    """Embedding configuration."""
    
    embedding_provider: str = Field(..., alias="embedding-provider")
    embedding_model: str = Field(..., alias="embedding-model")
    timeout: int = Field(default=60, ge=1)
    max_retries: int = Field(default=3, ge=1, alias="max-retries")
    database_path: str = Field(..., alias="database-path")
    ktop: int = Field(default=20, ge=1)


class Config(BaseModel):
    """Root configuration model."""
    
    llm: LLMConfig
    tech_trend_analysis: TechTrendAnalysisConfig = Field(
        ..., alias="tech-trend-analysis"
    )
    article_generator: ArticleGeneratorConfig = Field(
        ..., alias="article-generator"
    )
    embedding: EmbeddingConfig


def load_config(config_path: str = "./config.yaml") -> Config:
    """Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Validated Config object
        
    Raises:
        ConfigurationError: If config file is missing or invalid
    """
    path = Path(config_path)
    
    if not path.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}"
        )
    
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        return Config(**data)
    
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {e}")