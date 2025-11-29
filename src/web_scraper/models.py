# src/web_scraper/models.py
"""Data models for web scraper."""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class Trend:
    """Represents a single trend item."""
    topic: str
    reason: str
    links: List[str]
    search_keywords: List[str]


@dataclass
class TrendAnalysis:
    """Represents trend analysis input data."""
    analysis_date: str
    category: str
    trends: List[Trend]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrendAnalysis':
        """
        Create TrendAnalysis from dictionary.
        
        Args:
            data: Dictionary containing trend analysis data
            
        Returns:
            TrendAnalysis: Parsed trend analysis object
        """
        trends = [
            Trend(**trend) for trend in data.get('trends', [])
        ]
        return cls(
            analysis_date=data['analysis_date'],
            category=data['category'],
            trends=trends
        )


@dataclass
class ScrapedTrend:
    """Represents a scraped trend with content."""
    topic: str
    link: str
    content: str
    search_keywords: List[str]


@dataclass
class ScrapedOutput:
    """Represents final scraped output."""
    analysis_date: str
    category: str
    trends: List[ScrapedTrend]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            'analysis_date': self.analysis_date,
            'category': self.category,
            'trends': [asdict(trend) for trend in self.trends]
        }