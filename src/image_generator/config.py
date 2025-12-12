"""
Configuration management module.
"""
import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

from .exceptions import ConfigurationError


@dataclass
class ArticleGeneratorConfig:
    """Article generator configuration."""
    tech_trend_article: Path
    log: Path


@dataclass
class ImageGeneratorConfig:
    """Image generator configuration."""
    image_path: Path
    log: Path
    timeout: int
    retry: int
    provider: str
    llm_model: str
    default_size: int
    aspect_ratio: str
    style_instruction: str
    output_format: str


@dataclass
class Config:
    """Main configuration."""
    article_generator: ArticleGeneratorConfig
    image_generator: ImageGeneratorConfig


def load_config(config_path: Path = Path("config.yaml")) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration object
        
    Raises:
        ConfigurationError: If config file is missing or invalid
    """
    if not config_path.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}"
        )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to read config file: {e}")
    
    try:
        article_data = data.get('article-generator', {})
        article_config = ArticleGeneratorConfig(
            tech_trend_article=Path(
                article_data.get('tech-trend-article', 'data/tech-trend-article')
            ),
            log=Path(article_data.get('log', 'log/article-generator'))
        )
        
        img_data = data.get('image-generator', {})
        image_config = ImageGeneratorConfig(
            image_path=Path(img_data.get('image-path', 'data/image')),
            log=Path(img_data.get('log', 'log/image-generator')),
            timeout=img_data.get('timeout', 60),
            retry=img_data.get('retry', 3),
            provider=img_data.get('provider', 'Deepseek'),
            llm_model=img_data.get('llm-model', 'DeepSeek-V2.5'),
            default_size=img_data.get('default-size', 1024),
            aspect_ratio=img_data.get('aspect-ratio', '1:1'),
            style_instruction=img_data.get(
                'style-instruction',
                'Create a clean, modern illustration.'
            ),
            output_format=img_data.get('output-format', 'jpg')
        )
        
        return Config(
            article_generator=article_config,
            image_generator=image_config
        )
    
    except Exception as e:
        raise ConfigurationError(f"Invalid configuration structure: {e}")
