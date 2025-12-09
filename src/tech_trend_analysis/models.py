# ============================================================================
# src/tech_trend_analysis/models.py
# ============================================================================

"""Data models for tech trend analysis."""

from dataclasses import dataclass
from typing import List


@dataclass
class Article:
    """Represents an RSS article."""
    title: str
    link: str


@dataclass
class RSSFeed:
    """Represents an RSS feed category."""
    category: str
    feed_date: str
    article_count: int
    articles: List[Article]


@dataclass
class Trend:
    """Represents a technology trend."""
    topic: str
    reason: str
    score: int
    links: List[str]
    search_keywords: List[str]


@dataclass
class AnalysisReport:
    """Represents a trend analysis report."""
    feed_date: str
    category: str
    trends: List[Trend]