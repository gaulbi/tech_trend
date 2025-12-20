"""Data models for article publisher."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ImageMapping:
    """Image URL mapping data."""
    article_file: str
    category: str
    feed_date: str
    local_path: str
    imgbb_url: str
    uploaded_at: str
    status: str


@dataclass
class Article:
    """Article data."""
    title: str
    content: str
    category: str
    file_name: str
    file_path: str


@dataclass
class PublishResult:
    """Result of article publishing."""
    feed_date: str
    title: str
    published_datetime: str
    category: str
    article_url: str
    status: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "feed_date": self.feed_date,
            "title": self.title,
            "published_datetime": self.published_datetime,
            "category": self.category,
            "article_url": self.article_url,
            "status": self.status
        }


@dataclass
class HashnodeResponse:
    """Response from Hashnode API."""
    post_id: Optional[str]
    slug: Optional[str]
    title: Optional[str]
    errors: Optional[list]
    
    @property
    def is_success(self) -> bool:
        """Check if publishing was successful."""
        return self.post_id is not None and self.errors is None
    
    def get_url(self, base_domain: str = "hashnode.dev") -> Optional[str]:
        """
        Get article URL.
        
        Args:
            base_domain: Base domain for article URL
            
        Returns:
            Full article URL or None
        """
        if self.slug:
            return f"https://{base_domain}/{self.slug}"
        return None
