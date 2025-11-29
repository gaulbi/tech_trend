"""
URL Scraper Module

Handles fetching and cleaning content from URLs.
"""

import logging
import re
import time
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Comment
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class URLScraper:
    """
    Scrapes and cleans content from URLs.
    
    Uses BeautifulSoup for HTML parsing and cleaning.
    Implements retry logic and timeout handling.
    """
    
    def __init__(self, timeout: int = 60, max_retries: int = 3):
        """
        Initialize URL scraper with retry logic.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
        logger.info(f"URLScraper initialized (timeout={timeout}s, retries={max_retries})")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # Exponential backoff: 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set user agent to avoid blocking
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        return session
    
    def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape and clean content from a URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Cleaned text content or None if scraping fails
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Validate URL
            if not self._is_valid_url(url):
                logger.error(f"Invalid URL format: {url}")
                return None
            
            # Fetch content
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse and clean content
            content = self._clean_content(response.text, response.encoding)
            
            logger.info(f"Successfully scraped {len(content)} characters from {url}")
            return content
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while scraping {url} (timeout={self.timeout}s)")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {url}: {e}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}", exc_info=True)
            return None
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _clean_content(self, html: str, encoding: Optional[str] = None) -> str:
        """
        Clean HTML content and extract readable text.
        
        Removes:
        - HTML tags
        - Scripts and styles
        - Navigation elements
        - Excessive whitespace
        - Special characters and formatting
        
        Args:
            html: Raw HTML content
            encoding: Character encoding
            
        Returns:
            Cleaned text content
        """
        # Parse HTML with explicit parser (html.parser comes with Python standard library)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 
                            'aside', 'iframe', 'noscript', 'button']):
            element.decompose()
        
        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Get text content with stripping
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean text
        text = self._clean_text(text)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove reference indicators like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text
    
    def close(self) -> None:
        """Close the requests session."""
        self.session.close()
        logger.info("URLScraper session closed")