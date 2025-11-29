"""Data models and custom exceptions for RSS fetcher."""

from typing import Dict, List
from pydantic import BaseModel, Field


class ConfigurationError(Exception):
    """Raised when configuration file is missing or invalid."""
    pass


class ValidationError(Exception):
    """Raised when RSS list JSON is malformed."""
    pass


class RssConfig(BaseModel):
    """RSS configuration model."""
    rss_list: str = Field(..., alias="rss-list")
    rss_feed: str = Field(..., alias="rss-feed")
    log: str
    max_concurrent: int = Field(..., alias="max-concurrent")
    timeout: int
    retry: int


class Config(BaseModel):
    """Main configuration model."""
    rss: RssConfig


class Article(BaseModel):
    """Article data model."""
    title: str
    link: str


class CategoryOutput(BaseModel):
    """Output JSON structure for a category."""
    category: str
    fetch_date: str
    article_count: int
    articles: List[Article]