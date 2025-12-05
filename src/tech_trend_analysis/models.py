# ============================================================================
# FILE: src/tech_trend_analysis/models.py
# ============================================================================
"""Data models for tech trend analysis."""

from dataclasses import dataclass
from typing import List


@dataclass
class Article:
    """Represents a single RSS article."""
    title: str
    link: str


@dataclass
class RSSFeed:
    """Represents an RSS feed for a category."""
    category: str
    fetch_date: str
    article_count: int
    articles: List[Article]


@dataclass
class Trend:
    """Represents a single technology trend."""
    topic: str
    reason: str
    links: List[str]
    search_keywords: List[str]


@dataclass
class TrendAnalysis:
    """Represents complete trend analysis for a category."""
    analysis_date: str
    category: str
    trends: List[Trend]