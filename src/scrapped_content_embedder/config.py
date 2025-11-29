"""
Configuration management module.

Handles loading and validation of configuration from YAML files.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import yaml


@dataclass
class ScrapConfig:
    """Scraping configuration."""
    url_scrapped_content: Path
    
    
@dataclass
class EmbeddingConfig:
    """Embedding configuration."""
    chunk_size: int
    chunk_overlap: int
    embedding_provider: str
    embedding_model: str
    timeout: int
    database_path: Path


@dataclass
class Config:
    """Main configuration class."""
    scrap: ScrapConfig
    embedding: EmbeddingConfig
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config.yaml file
            
        Returns:
            Config instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Validate required fields
        if 'scrap' not in data or 'embedding' not in data:
            raise ValueError("Config must contain 'scrap' and 'embedding' sections")
        
        scrap_config = ScrapConfig(
            url_scrapped_content=Path(data['scrap']['url-scrapped-content'])
        )
        
        embedding_config = EmbeddingConfig(
            chunk_size=data['embedding']['chunk-size'],
            chunk_overlap=data['embedding']['chunk-overlap'],
            embedding_provider=data['embedding']['embedding-provider'],
            embedding_model=data['embedding']['embedding-model'],
            timeout=data['embedding']['timeout'],
            database_path=Path(data['embedding']['database-path'])
        )
        
        return cls(scrap=scrap_config, embedding=embedding_config)