"""Data models for tech trend analysis."""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Article:
    """Represents a single article from RSS feed."""
    title: str
    link: str


@dataclass
class RSSFeed:
    """Represents an RSS feed for a category."""
    category: str
    fetch_date: str
    article_count: int
    articles: List[Article]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RSSFeed":
        """Create RSSFeed from dictionary.
        
        Args:
            data: Dictionary containing RSS feed data
            
        Returns:
            RSSFeed instance
        """
        articles = [
            Article(title=a["title"], link=a["link"]) 
            for a in data["articles"]
        ]
        return cls(
            category=data["category"],
            fetch_date=data["fetch_date"],
            article_count=data["article_count"],
            articles=articles
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert RSSFeed to dictionary.
        
        Returns:
            Dictionary representation of RSS feed
        """
        return {
            "category": self.category,
            "fetch_date": self.fetch_date,
            "article_count": self.article_count,
            "articles": [
                {"title": a.title, "link": a.link} 
                for a in self.articles
            ]
        }


@dataclass
class Trend:
    """Represents a single technology trend."""
    topic: str
    reason: str
    category: str
    links: List[str]
    search_keywords: List[str]


@dataclass
class AnalysisReport:
    """Represents the complete analysis report for a category."""
    analysis_date: str
    category: str
    trends: List[Trend]

    def to_dict(self) -> Dict[str, Any]:
        """Convert AnalysisReport to dictionary.
        
        Returns:
            Dictionary representation of analysis report
        """
        return {
            "analysis_date": self.analysis_date,
            "category": self.category,
            "trends": [
                {
                    "topic": t.topic,
                    "reason": t.reason,
                    "links": t.links,
                    "search_keywords": t.search_keywords
                }
                for t in self.trends
            ]
        }