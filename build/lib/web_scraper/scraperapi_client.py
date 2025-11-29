"""
ScraperAPI Client Implementation

Implements web scraping using ScraperAPI service.
"""

import logging
import requests
from typing import List, Dict, Any

from .scraper_base import (
    ScraperBase, 
    ScraperError, 
    ScraperTimeoutError,
    ScraperAuthenticationError,
    ScraperRateLimitError
)

logger = logging.getLogger(__name__)


class ScraperAPIClient(ScraperBase):
    """
    ScraperAPI implementation for web scraping.
    
    Uses ScraperAPI service to scrape websites and perform searches.
    """
    
    BASE_URL = "https://api.scraperapi.com"
    GOOGLE_SEARCH_URL = "https://api.scraperapi.com/structured/google/search"
    
    def __init__(self, api_key: str, timeout: int = 60):
        """
        Initialize ScraperAPI client.
        
        Args:
            api_key: ScraperAPI API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        logger.info(f"Initialized ScraperAPI client with timeout={timeout}s")
    
    def scrape_url(self, url: str) -> str:
        """
        Scrape content from a URL using ScraperAPI.
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped HTML content
            
        Raises:
            ScraperError: If scraping fails
        """
        logger.info(f"Scraping URL with ScraperAPI: {url}")
        
        params = {
            'api_key': self.api_key,
            'url': url,
            'render': 'false'
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
        Perform web search using ScraperAPI's Google Search structured endpoint.
        
        Args:
            query: Search query
            
        Returns:
            List of search results with 'url' and 'title' keys
            
        Raises:
            ScraperError: If search fails
        """
        logger.info(f"Searching with ScraperAPI: {query}")
        
        params = {
            'api_key': self.api_key,
            'query': query,
            'num': '5'  # Limit to top 5 results
        }
        
        try:
            response = requests.get(
                self.GOOGLE_SEARCH_URL,
                params=params,
                timeout=self.timeout
            )
            
            self._handle_response(response)
            
            # Parse JSON response from structured endpoint
            data = response.json()
            results = []
            
            # Extract organic results
            organic_results = data.get('organic_results', [])
            for result in organic_results[:5]:  # Top 5 results
                results.append({
                    'url': result.get('link', ''),
                    'title': result.get('title', 'No title')
                })
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except requests.Timeout:
            raise ScraperTimeoutError(f"Timeout searching for '{query}'")
        except requests.RequestException as e:
            raise ScraperError(f"Search failed for '{query}': {str(e)}")
        except (KeyError, ValueError) as e:
            raise ScraperError(f"Failed to parse search results: {str(e)}")
    
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
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "ScraperAPI"