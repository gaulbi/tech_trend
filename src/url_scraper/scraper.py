"""
URL scraping and content extraction module.
"""

import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup, Comment
from readability import Document

from .logger import get_logger


class URLScraper:
    """Handles URL scraping with retry logic and content cleaning."""
    
    MAX_RETRIES = 3
    BACKOFF_DELAYS = [1, 2, 4]  # Exponential backoff in seconds
    
    def __init__(self, timeout: int):
        """
        Initialize scraper.
        
        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.logger = get_logger(__name__)
    
    def scrape(self, url: str) -> Optional[str]:
        """
        Scrape and clean content from URL with retry logic.
        
        Args:
            url: URL to scrape.
            
        Returns:
            Cleaned text content, or None if scraping failed.
        """
        self.logger.info(f"Scraping: {url}")
        
        html = self._fetch_with_retry(url)
        if not html:
            return None
        
        content = self._extract_clean_content(html)
        self.logger.info(f"Successfully scraped: {url}")
        
        return content
    
    def _fetch_with_retry(self, url: str) -> Optional[str]:
        """
        Fetch URL with exponential backoff retry.
        
        Args:
            url: URL to fetch.
            
        Returns:
            HTML content or None if all retries failed.
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                response.raise_for_status()
                return response.text
                
            except requests.Timeout:
                self._handle_retry_error(
                    url, attempt, "Timeout"
                )
            except requests.RequestException as e:
                self._handle_retry_error(
                    url, attempt, f"Request error: {e}"
                )
            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching {url}: {e}",
                    exc_info=True
                )
                return None
            
            if attempt < self.MAX_RETRIES - 1:
                time.sleep(self.BACKOFF_DELAYS[attempt])
        
        self.logger.error(
            f"Failed to fetch {url} after {self.MAX_RETRIES} attempts"
        )
        return None
    
    def _handle_retry_error(
        self, 
        url: str, 
        attempt: int, 
        error_msg: str
    ) -> None:
        """
        Handle retry errors with appropriate logging.
        
        Args:
            url: URL being fetched.
            attempt: Current attempt number (0-indexed).
            error_msg: Error message.
        """
        if attempt < self.MAX_RETRIES - 1:
            self.logger.warning(
                f"{error_msg} for {url}, "
                f"retrying ({attempt + 1}/{self.MAX_RETRIES})..."
            )
        else:
            self.logger.error(
                f"{error_msg} for {url}, "
                f"all retries exhausted"
            )
    
    def _extract_clean_content(self, html: str) -> str:
        """
        Extract and clean readable content from HTML.
        
        Args:
            html: Raw HTML content.
            
        Returns:
            Cleaned text content.
        """
        # Use readability to extract main content
        doc = Document(html)
        content_html = doc.summary()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(content_html, 'html.parser')
        
        # Sanitize: Remove unwanted tags
        self._remove_unwanted_tags(soup)
        
        # Extract text
        text = soup.get_text()
        
        # Normalize whitespace
        text = self._normalize_whitespace(text)
        
        return text
    
    def _remove_unwanted_tags(self, soup: BeautifulSoup) -> None:
        """
        Remove unwanted HTML tags from soup.
        
        Args:
            soup: BeautifulSoup object to clean (modified in-place).
        """
        unwanted_tags = ['script', 'style', 'meta', 'noscript']
        
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove HTML comments
        for comment in soup.find_all(
            string=lambda text: isinstance(text, Comment)
        ):
            comment.extract()
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Text to normalize.
            
        Returns:
            Normalized text.
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline (paragraph)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
