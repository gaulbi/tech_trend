"""
Configuration Loader Module

Handles loading and validation of YAML configuration files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass
class LLMConfig:
    """LLM configuration."""
    server: str
    model: str
    timeout: int


@dataclass
class EmbeddingConfig:
    """Embedding configuration."""
    chunk_size: int
    chunk_overlap: int
    provider: str
    model: str
    timeout: int
    max_retries: int
    batch_size: int
    database_path: str
    ktop: int


@dataclass
class PathsConfig:
    """File paths configuration."""
    analysis_report: str
    system_prompt: str
    user_prompt: str
    tech_trend_article: str


@dataclass
class Config:
    """Main configuration container."""
    llm: LLMConfig
    embedding: EmbeddingConfig
    paths: PathsConfig
    api_keys: Dict[str, str]


class ConfigLoader:
    """Loads and validates configuration from YAML file."""
    
    @staticmethod
    def load_config(config_path: str = 'config.yaml') -> Config:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Config object with all settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        # Load environment variables
        load_dotenv()
        
        # Load YAML configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            yaml_config = yaml.safe_load(f)
        
        # Parse LLM configuration
        llm_config = LLMConfig(
            server=yaml_config['llm']['server'],
            model=yaml_config['llm']['llm-model'],
            timeout=yaml_config['llm'].get('timeout', 60)
        )
        
        # Parse embedding configuration
        embedding_config = EmbeddingConfig(
            chunk_size=yaml_config['embedding']['chunk-size'],
            chunk_overlap=yaml_config['embedding']['chunk-overlap'],
            provider=yaml_config['embedding']['embedding-provider'],
            model=yaml_config['embedding']['embedding-model'],
            timeout=yaml_config['embedding'].get('timeout', 60),
            max_retries=yaml_config['embedding'].get('max-retries', 3),
            batch_size=yaml_config['embedding'].get('batch-size', 50),
            database_path=yaml_config['embedding']['database-path'],
            ktop=yaml_config['embedding'].get('ktop', 20)
        )
        
        # Parse paths configuration
        paths_config = PathsConfig(
            analysis_report=yaml_config['tech-trend-analysis']['analysis-report'],
            system_prompt=yaml_config['article-generator']['system-prompt'],
            user_prompt=yaml_config['article-generator']['user-prompt'],
            tech_trend_article=yaml_config['article-generator']['tech-trend-article']
        )
        
        # Load API keys from environment
        api_keys = {
            'openai': os.getenv('OPENAI_API_KEY', ''),
            'deepseek': os.getenv('DEEPSEEK_API_KEY', ''),
            'claude': os.getenv('CLAUDE_API_KEY', ''),
            'voyage': os.getenv('VOYAGE_API_KEY', ''),
            'gemini': os.getenv('GEMINI_API_KEY', '')
        }
        
        config = Config(
            llm=llm_config,
            embedding=embedding_config,
            paths=paths_config,
            api_keys=api_keys
        )
        
        # Validate configuration
        ConfigLoader._validate_config(config)
        
        return config
    
    @staticmethod
    def _validate_config(config: Config) -> None:
        """
        Validate configuration values.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate LLM server
        valid_servers = ['openai', 'deepseek', 'claude', 'ollama']
        if config.llm.server not in valid_servers:
            raise ValueError(
                f"Invalid LLM server: {config.llm.server}. "
                f"Must be one of: {valid_servers}"
            )
        
        # Validate API key for non-local providers
        if config.llm.server != 'ollama':
            api_key = config.api_keys.get(config.llm.server)
            if not api_key:
                raise ValueError(
                    f"API key not found for {config.llm.server}. "
                    f"Please set {config.llm.server.upper()}_API_KEY in .env file"
                )
        
        # Validate embedding provider
        valid_embedding_providers = ['openai', 'voyage', 'gemini', 'sentence-transformers']
        if config.embedding.provider not in valid_embedding_providers:
            raise ValueError(
                f"Invalid embedding provider: {config.embedding.provider}. "
                f"Must be one of: {valid_embedding_providers}"
            )
        
        # Validate paths exist
        if not Path(config.paths.system_prompt).exists():
            raise ValueError(f"System prompt file not found: {config.paths.system_prompt}")
        
        if not Path(config.paths.user_prompt).exists():
            raise ValueError(f"User prompt file not found: {config.paths.user_prompt}")