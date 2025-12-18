"""
Data models for tech trends and deduplication.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class TechTrend:
    """Represents a single tech trend."""
    
    topic: str
    reason: str
    score: int
    links: List[str]
    search_keywords: List[str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "topic": self.topic,
            "reason": self.reason,
            "score": self.score,
            "links": self.links,
            "search_keywords": self.search_keywords,
        }
    
    def get_embedding_text(self) -> str:
        """
        Get text for embedding generation.
        
        Returns:
            Formatted text combining topic and keywords
        """
        if not self.search_keywords:
            # If no keywords, just use topic
            return f"Topic: {self.topic}"
        keywords = ", ".join(self.search_keywords)
        return f"Topic: {self.topic}. Keywords: {keywords}"
    
    @classmethod
    def from_dict(cls, data: dict) -> "TechTrend":
        """
        Create TechTrend from dictionary.
        
        Args:
            data: Dictionary with trend data
            
        Returns:
            TechTrend instance
        """
        return cls(
            topic=data["topic"],
            reason=data["reason"],
            score=data["score"],
            links=data["links"],
            search_keywords=data["search_keywords"],
        )


@dataclass
class TrendAnalysis:
    """Represents a complete trend analysis for a category."""
    
    feed_date: str
    category: str
    trends: List[TechTrend]
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "feed_date": self.feed_date,
            "category": self.category,
            "trends": [t.to_dict() for t in self.trends],
        }
    
    def get_sorted_trends(self) -> List[TechTrend]:
        """
        Get trends sorted by score (descending).
        
        Returns:
            List of trends sorted by impact score
        """
        return sorted(self.trends, key=lambda t: t.score, reverse=True)
    
    @classmethod
    def from_dict(cls, data: dict) -> "TrendAnalysis":
        """
        Create TrendAnalysis from dictionary.
        
        Args:
            data: Dictionary with analysis data
            
        Returns:
            TrendAnalysis instance
        """
        trends = [TechTrend.from_dict(t) for t in data["trends"]]
        return cls(
            feed_date=data["feed_date"],
            category=data["category"],
            trends=trends,
        )


@dataclass
class DuplicateMatch:
    """Represents a duplicate match result."""
    
    matched_topic: str
    matched_date: str
    similarity_score: float
    
    def __str__(self) -> str:
        """String representation of duplicate match."""
        return (
            f"'{self.matched_topic}' from {self.matched_date} "
            f"(Score: {self.similarity_score:.2f})"
        )
