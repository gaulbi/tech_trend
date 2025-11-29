# src/web_scraper/scraper_factory.py
"""Factory for creating web scraper clients."""

import logging
from typing import Optional

from .scraper_base import BaseWebScraper
from .scraper_clients import (
    ScraperAPIClient,
    ScrapingBeeClient,
    ZenRowsClient
)
from .config import Config


logger = logging.getLogger(__name__)


class ScraperFactory:
    """Factory for creating appropriate web scraper client."""
    
    @staticmethod
    def create_scraper(config: Config) -> Optional[BaseWebScraper]:
        """
        Create a web scraper client based on available API keys.
        Priority: ScraperAPI > ScrapingBee > ZenRows
        
        Args:
            config: Configuration object
            
        Returns:
            Optional[BaseWebScraper]: Scraper client or None
        """
        if config.scraperapi_key:
            logger.info("Using ScraperAPI")
            try:
                return ScraperAPIClient(
                    config.scraperapi_key, 
                    config.timeout
                )
            except ValueError as e:
                logger.error(f"ScraperAPI initialization failed: {e}")
        
        if config.scrapingbee_key:
            logger.info("Using ScrapingBee")
            try:
                return ScrapingBeeClient(
                    config.scrapingbee_key, 
                    config.timeout
                )
            except ValueError as e:
                logger.error(f"ScrapingBee initialization failed: {e}")
        
        if config.zenrows_key:
            logger.info("Using ZenRows")
            try:
                return ZenRowsClient(
                    config.zenrows_key, 
                    config.timeout
                )
            except ValueError as e:
                logger.error(f"ZenRows initialization failed: {e}")
        
        logger.error("No valid scraper API key found in environment")
        return None