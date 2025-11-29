"""Data models for tech trend analysis."""

from dataclasses import dataclass
from typing import List


@dataclass
class Article:
    """RSS article data."""
    title: str
    link: str


@dataclass
class RSSFeed:
    """RSS feed data."""
    category: str
    fetch_date: str
    article_count: int
    articles: List[Article]


@dataclass
class Trend:
    """Technology trend data."""
    topic: str
    reason: str
    links: List[str]
    search_keywords: List[str]


@dataclass
class TrendAnalysis:
    """Tech trend analysis report."""
    analysis_date: str
    category: str
    trends: List[Trend]