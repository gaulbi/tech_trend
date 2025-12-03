# src/web_scraper/scraper_clients/base.py
"""Abstract base class for scraper clients."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseScraperClient(ABC):
    """Abstract base class for web scraper API clients."""
    
    def __init__(self, api_key: str, timeout: int = 60):
        """
        Initialize scraper client.
        
        Args:
            api_key: API key for the scraper service
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
    
    @abstractmethod
    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch content from URL using scraper API.
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content or None if failed
        """
        pass