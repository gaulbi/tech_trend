"""
Data models for URL scraper.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class TrendItem:
    """Represents a single trend item from analysis."""
    
    topic: str
    reason: str
    score: int
    links: List[str]
    search_keywords: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrendItem":
        """
        Create TrendItem from dictionary.
        
        Args:
            data: Dictionary with trend data.
            
        Returns:
            TrendItem instance.
        """
        return cls(
            topic=data["topic"],
            reason=data["reason"],
            score=data["score"],
            links=data["links"],
            search_keywords=data["search_keywords"]
        )


@dataclass
class TrendAnalysis:
    """Represents tech trend analysis input."""
    
    feed_date: str
    category: str
    trends: List[TrendItem]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrendAnalysis":
        """
        Create TrendAnalysis from dictionary.
        
        Args:
            data: Dictionary with analysis data.
            
        Returns:
            TrendAnalysis instance.
        """
        trends = [
            TrendItem.from_dict(t) for t in data.get("trends", [])
        ]
        return cls(
            feed_date=data["feed_date"],
            category=data["category"],
            trends=trends
        )


@dataclass
class ScrapedTrendItem:
    """Represents a scraped trend item."""
    
    topic: str
    query_used: str
    search_link: str
    content: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "topic": self.topic,
            "query_used": self.query_used,
            "search_link": self.search_link,
            "content": self.content
        }


@dataclass
class ScrapedContent:
    """Represents scraped content output."""
    
    feed_date: str
    category: str
    trends: List[ScrapedTrendItem]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation.
        """
        return {
            "feed_date": self.feed_date,
            "category": self.category,
            "trends": [t.to_dict() for t in self.trends]
        }
