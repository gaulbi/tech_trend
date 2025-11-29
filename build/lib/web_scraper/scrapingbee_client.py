"""
ScrapingBee Client Implementation

Implements web scraping using ScrapingBee service.
"""

import logging
import requests
from typing import List, Dict, Any
from urllib.parse import urlencode

from .scraper_base import (
    ScraperBase,
    ScraperError,
    ScraperTimeoutError,
    ScraperAuthenticationError,
    ScraperRateLimitError
)

logger = logging.getLogger(__name__)


class ScrapingBeeClient(ScraperBase):
    """
    ScrapingBee implementation for web scraping.
    
    Uses ScrapingBee service to scrape websites and perform searches.
    Note: ScrapingBee does not have a native Google Search API,
    so we scrape Google's search page and parse results.
    """
    
    BASE_URL = "https://app.scrapingbee.com/api/v1"
    
    def __init__(self, api_key: str, timeout: int = 60):
        """
        Initialize ScrapingBee client.
        
        Args:
            api_key: ScrapingBee API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        logger.info(f"Initialized ScrapingBee client with timeout={timeout}s")
    
    def scrape_url(self, url: str) -> str:
        """
        Scrape content from a URL using ScrapingBee.
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped HTML content
            
        Raises:
            ScraperError: If scraping fails
        """
        logger.info(f"Scraping URL with ScrapingBee: {url}")
        
        params = {
            'api_key': self.api_key,
            'url': url,
            'render_js': 'false'
        }
        
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            
            self._handle_response(response)
            
            logger.info(f"Successfully scraped {len(response.text)} characters from {url}")
            return response.text
            
        except requests.Timeout:
            raise ScraperTimeoutError(f"Timeout scraping {url}")
        except requests.RequestException as e:
            raise ScraperError(f"Request failed for {url}: {str(e)}")
    
    def search_web(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search by scraping Google Search results page.
        
        Args:
            query: Search query
            
        Returns:
            List of search results with 'url' and 'title' keys
            
        Raises:
            ScraperError: If search fails
        """
        logger.info(f"Searching with ScrapingBee: {query}")
        
        # Build Google search URL
        google_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=10"
        
        params = {
            'api_key': self.api_key,
            'url': google_url,
            'render_js': 'false'
        }
        
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            
            self._handle_response(response)
            
            # Parse search results from HTML
            results = self._parse_google_results(response.text)
            logger.info(f"Found {len(results)} search results")
            
            return results
            
        except requests.Timeout:
            raise ScraperTimeoutError(f"Timeout searching for '{query}'")
        except requests.RequestException as e:
            raise ScraperError(f"Search failed for '{query}': {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> None:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
            
        Raises:
            ScraperAuthenticationError: If authentication fails
            ScraperRateLimitError: If rate limit is exceeded
            ScraperError: For other errors
        """
        if response.status_code == 401:
            raise ScraperAuthenticationError("Invalid API key")
        elif response.status_code == 429:
            raise ScraperRateLimitError("Rate limit exceeded")
        elif response.status_code != 200:
            raise ScraperError(
                f"API returned status {response.status_code}: {response.text[:200]}"
            )
    
    def _parse_google_results(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse Google search results from HTML.
        
        Args:
            html: HTML content from Google search
            
        Returns:
            List of search results with 'url' and 'title' keys
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Modern Google uses <div class="g"> for search results
        # Try multiple selectors for robustness
        result_divs = soup.select('div.g, div[data-hveid]')
        
        for div in result_divs:
            # Find the main link
            link_elem = div.select_one('a[href^="http"], a[href^="/url?"]')
            
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                
                # Clean up Google redirect URLs
                if href.startswith('/url?'):
                    # Extract actual URL from Google redirect
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    href = parsed.get('q', [href])[0]
                
                # Skip non-http URLs
                if not href.startswith('http'):
                    continue
                
                # Get title - try multiple selectors
                title_elem = div.select_one('h3, div[role="heading"]')
                title = title_elem.get_text(strip=True) if title_elem else 'No title'
                
                results.append({
                    'url': href,
                    'title': title
                })
                
                if len(results) >= 5:  # Limit to top 5 results
                    break
        
        return results
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "ScrapingBee"