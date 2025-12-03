# src/web_scraper/scraper_clients/scrapingbee.py
"""ScrapingBee client implementation."""

import time
from typing import Optional
import requests

from .base import BaseScraperClient


class ScrapingBeeClient(BaseScraperClient):
    """Client for ScrapingBee service."""
    
    BASE_URL = "https://app.scrapingbee.com/api/v1/"
    MAX_RETRIES = 3
    BACKOFF_DELAYS = [1, 2, 4]
    
    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch content from URL using ScrapingBee.
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content or None if all retries failed
        """
        params = {
            'api_key': self.api_key,
            'url': url
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.text
                
            except requests.exceptions.Timeout:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.BACKOFF_DELAYS[attempt])
                    continue
                return None
                
            except requests.exceptions.RequestException:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.BACKOFF_DELAYS[attempt])
                    continue
                return None
        
        return None