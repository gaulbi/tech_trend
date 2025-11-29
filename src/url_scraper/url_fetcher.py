"""URL fetching with retry logic."""

import time
import logging
from typing import Optional
import requests
from requests.exceptions import RequestException, Timeout


class URLFetcher:
    """Fetch URLs with retry and timeout logic."""
    
    MAX_RETRIES = 3
    BACKOFF_DELAYS = [1, 2, 4]  # Exponential backoff in seconds
    
    def __init__(self, timeout: int, logger: logging.Logger):
        """
        Initialize URL fetcher.
        
        Args:
            timeout: Request timeout in seconds
            logger: Logger instance
        """
        self.timeout = timeout
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        })
    
    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch content from URL with retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            Optional[str]: HTML content if successful, None otherwise
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(
                    url, 
                    timeout=self.timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                self.logger.info(f"Successfully fetched: {url}")
                return response.text
                
            except Timeout:
                self._handle_retry(url, attempt, "Timeout")
            except RequestException as e:
                self._handle_retry(url, attempt, f"Request error: {e}")
            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching {url}: {e}"
                )
                return None
        
        self.logger.error(
            f"Failed to fetch {url} after {self.MAX_RETRIES} attempts"
        )
        return None
    
    def _handle_retry(
        self, 
        url: str, 
        attempt: int, 
        error_msg: str
    ) -> None:
        """
        Handle retry logic with backoff.
        
        Args:
            url: URL being fetched
            attempt: Current attempt number (0-indexed)
            error_msg: Error message to log
        """
        if attempt < self.MAX_RETRIES - 1:
            delay = self.BACKOFF_DELAYS[attempt]
            self.logger.warning(
                f"{error_msg} for {url}. Retrying in {delay}s "
                f"(attempt {attempt + 1}/{self.MAX_RETRIES})"
            )
            time.sleep(delay)
        else:
            self.logger.error(
                f"{error_msg} for {url}. No more retries."
            )
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()