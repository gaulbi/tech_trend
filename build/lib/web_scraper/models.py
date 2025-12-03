# src/web_scraper/models.py
"""Data models for web scraper."""

from dataclasses import dataclass
from typing import List


@dataclass
class Trend:
    """Represents a single trend from input."""
    topic: str
    reason: str
    links: List[str]
    search_keywords: List[str]


@dataclass
class InputData:
    """Represents input analysis file."""
    analysis_date: str
    category: str
    trends: List[Trend]


@dataclass
class ScrapedTrend:
    """Represents a scraped trend for output."""
    topic: str
    query_used: str
    link: str
    content: str
    source_search_terms: List[str]


@dataclass
class OutputData:
    """Represents output scraped file."""
    analysis_date: str
    category: str
    trends: List[ScrapedTrend]