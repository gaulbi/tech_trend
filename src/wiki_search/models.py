"""
Data models for wiki_search module.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TrendInput:
    """Represents a single trend from input data."""
    topic: str
    reason: str
    score: int
    links: List[str]
    search_keywords: List[str]


@dataclass
class TrendAnalysis:
    """Represents input trend analysis data."""
    feed_date: str
    category: str
    trends: List[TrendInput]


@dataclass
class TrendOutput:
    """Represents a single trend in output data."""
    topic: str
    query_used: str
    search_link: str
    content: str


@dataclass
class ScrapedContent:
    """Represents output scraped content data."""
    feed_date: str
    category: str
    trends: List[TrendOutput]