"""Data models for URL scraper."""

from typing import List
from dataclasses import dataclass


@dataclass
class TrendInput:
    """Input trend from tech trend analysis."""
    topic: str
    reason: str
    links: List[str]
    search_keywords: List[str]


@dataclass
class TrendOutput:
    """Output trend with scraped content."""
    topic: str
    link: str
    content: str
    search_keywords: List[str]


@dataclass
class AnalysisInput:
    """Input analysis file structure."""
    analysis_date: str
    category: str
    trends: List[TrendInput]


@dataclass
class AnalysisOutput:
    """Output analysis file structure."""
    analysis_date: str
    category: str
    trends: List[TrendOutput]