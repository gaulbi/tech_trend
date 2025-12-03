# src/web_scraper/scraper_factory.py
"""Factory for creating scraper clients."""

import os
from typing import Optional

from dotenv import load_dotenv

from .scraper_clients import (
    BaseScraperClient,
    ScraperAPIClient,
    ScrapingBeeClient,
    ZenRowsClient
)
from .exceptions import ConfigurationError


class ScraperFactory:
    """Factory for creating appropriate scraper client."""
    
    def __init__(self):
        """Initialize factory and load environment variables."""
        load_dotenv()
    
    def create_client(self, timeout: int = 60) -> BaseScraperClient:
        """
        Create scraper client based on available API keys.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            Configured scraper client instance
            
        Raises:
            ConfigurationError: If no valid API key found
        """
        # Try ScraperAPI first
        api_key = os.getenv('SCRAPERAPI_KEY')
        if api_key:
            return ScraperAPIClient(api_key=api_key, timeout=timeout)
        
        # Try ScrapingBee
        api_key = os.getenv('SCRAPINGBEE_KEY')
        if api_key:
            return ScrapingBeeClient(api_key=api_key, timeout=timeout)
        
        # Try ZenRows
        api_key = os.getenv('ZENROWS_KEY')
        if api_key:
            return ZenRowsClient(api_key=api_key, timeout=timeout)
        
        raise ConfigurationError(
            "No scraper API key found in .env file. "
            "Please set SCRAPERAPI_KEY, SCRAPINGBEE_KEY, or ZENROWS_KEY"
        )