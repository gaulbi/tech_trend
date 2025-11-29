# src/web_scraper/scraper_clients.py
"""Web scraper client implementations."""

from typing import Dict, Any

from .scraper_base import BaseWebScraper


class ScraperAPIClient(BaseWebScraper):
    """ScraperAPI client implementation."""
    
    BASE_URL = "http://api.scraperapi.com"
    
    def _get_api_url(self) -> str:
        """Get the API URL for ScraperAPI."""
        return self.BASE_URL
    
    def _build_request_params(self, url: str) -> Dict[str, Any]:
        """
        Build request parameters for ScraperAPI.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict[str, Any]: Request parameters
        """
        return {
            'api_key': self.api_key,
            'url': url
        }


class ScrapingBeeClient(BaseWebScraper):
    """ScrapingBee client implementation."""
    
    BASE_URL = "https://app.scrapingbee.com/api/v1"
    
    def _get_api_url(self) -> str:
        """Get the API URL for ScrapingBee."""
        return self.BASE_URL
    
    def _build_request_params(self, url: str) -> Dict[str, Any]:
        """
        Build request parameters for ScrapingBee.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict[str, Any]: Request parameters
        """
        return {
            'api_key': self.api_key,
            'url': url
        }


class ZenRowsClient(BaseWebScraper):
    """ZenRows client implementation."""
    
    BASE_URL = "https://api.zenrows.com/v1"
    
    def _get_api_url(self) -> str:
        """Get the API URL for ZenRows."""
        return self.BASE_URL
    
    def _build_request_params(self, url: str) -> Dict[str, Any]:
        """
        Build request parameters for ZenRows.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict[str, Any]: Request parameters
        """
        return {
            'apikey': self.api_key,
            'url': url
        }
