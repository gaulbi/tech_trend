# src/web_scraper/scraper_base.py
"""Abstract base class for web scraper implementations."""

import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import requests


logger = logging.getLogger(__name__)


class BaseWebScraper(ABC):
    """Abstract base class for web scraper clients."""
    
    MAX_RETRIES = 3
    BACKOFF_DELAYS = [1, 2, 4]
    
    def __init__(self, api_key: str, timeout: int = 60) -> None:
        """
        Initialize scraper with API key and timeout.
        
        Args:
            api_key: API key for the scraper service
            timeout: Request timeout in seconds
            
        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.timeout = timeout
    
    @abstractmethod
    def _build_request_params(self, url: str) -> Dict[str, Any]:
        """
        Build request parameters for the specific scraper API.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict[str, Any]: Request parameters
        """
        pass
    
    @abstractmethod
    def _get_api_url(self) -> str:
        """
        Get the API URL for the scraper service.
        
        Returns:
            str: API URL
        """
        pass
    
    def scrape(self, url: str) -> Optional[str]:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Optional[str]: Scraped HTML content or None if failed
        """
        params = self._build_request_params(url)
        api_url = self._get_api_url()
        return self._scrape_with_retry(api_url, params)
    
    def _scrape_with_retry(
        self, 
        api_url: str, 
        params: Dict[str, Any]
    ) -> Optional[str]:
        """
        Execute scrape request with exponential backoff retry logic.
        
        Args:
            api_url: API endpoint URL
            params: Request parameters
            
        Returns:
            Optional[str]: Response content or None
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(
                    api_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.text
                
            except requests.exceptions.Timeout:
                logger.warning(
                    f"Timeout on attempt {attempt + 1}/{self.MAX_RETRIES}"
                )
                self._handle_retry(attempt)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                self._handle_retry(attempt)
        
        return None
    
    def _handle_retry(self, attempt: int) -> None:
        """
        Handle retry delay between attempts.
        
        Args:
            attempt: Current attempt number (0-indexed)
        """
        if attempt < self.MAX_RETRIES - 1:
            delay = self.BACKOFF_DELAYS[attempt]
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)