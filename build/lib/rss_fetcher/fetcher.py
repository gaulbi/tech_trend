"""RSS feed fetcher and parser."""

import feedparser
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Article:
    """Represents a single RSS article."""
    
    def __init__(
        self,
        title: str,
        link: str,
        published: str,
        source: str
    ):
        self.title = title
        self.link = link
        self.published = published
        self.source = source
    
    def to_dict(self) -> Dict[str, str]:
        """Convert article to dictionary."""
        return {
            "title": self.title,
            "link": self.link,
            "published": self.published,
            "source": self.source
        }


class RSSFetcher:
    """Fetches and parses RSS feeds."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize RSS fetcher.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def fetch_feed(self, url: str, source_name: str) -> List[Article]:
        """
        Fetch and parse a single RSS feed.
        
        Args:
            url: RSS feed URL
            source_name: Human-readable source name
            
        Returns:
            List of Article objects
        """
        try:
            logger.info(f"Fetching feed from {source_name}: {url}")
            feed = feedparser.parse(url)
            
            if feed.bozo and not feed.entries:
                logger.error(f"Failed to parse feed from {source_name}: {feed.bozo_exception}")
                return []
            
            articles = []
            for entry in feed.entries:
                article = self._parse_entry(entry, source_name)
                if article:
                    articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching feed from {source_name}: {e}")
            return []
    
    def _parse_entry(self, entry: feedparser.FeedParserDict, source_name: str) -> Optional[Article]:
        """
        Parse a single feed entry into an Article.
        
        Args:
            entry: Feed entry from feedparser
            source_name: Source name for attribution
            
        Returns:
            Article object or None if parsing fails
        """
        try:
            # Extract title
            title = entry.get('title', 'No title')
            
            # Extract link
            link = entry.get('link', '')
            
            # Extract published date
            published = self._get_published_date(entry)
            
            return Article(
                title=title,
                link=link,
                published=published,
                source=source_name
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse entry from {source_name}: {e}")
            return None
    
    def _get_published_date(self, entry: feedparser.FeedParserDict) -> str:
        """
        Extract published date from entry.
        
        Args:
            entry: Feed entry
            
        Returns:
            Published date string
        """
        # Try different date fields
        if hasattr(entry, 'published'):
            return entry.published
        elif hasattr(entry, 'updated'):
            return entry.updated
        elif hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            dt = datetime(*entry.updated_parsed[:6])
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        else:
            return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    def fetch_category(
        self,
        sources: Dict[str, str],
        category: str
    ) -> Dict[str, any]:
        """
        Fetch all feeds for a category.
        
        Args:
            sources: Dictionary mapping source names to URLs
            category: Category name
            
        Returns:
            Dictionary with category data and articles
        """
        all_articles = []
        
        for source_name, url in sources.items():
            articles = self.fetch_feed(url, source_name)
            all_articles.extend(articles)
        
        return {
            "category": category,
            "fetch_timestamp": datetime.now().isoformat(),
            "article_count": len(all_articles),
            "articles": [article.to_dict() for article in all_articles]
        }