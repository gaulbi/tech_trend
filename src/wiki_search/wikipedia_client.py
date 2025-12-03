"""
Wikipedia API client with retry logic for wiki_search module.
"""

import logging
import time
from typing import List, Optional, Tuple

import wikipedia


class WikipediaClient:
    """Client for interacting with Wikipedia API."""
    
    def __init__(self, timeout: int = 60, max_retries: int = 3):
        """
        Initialize Wikipedia client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        # Note: wikipedia library uses requests internally
        # Timeout is not directly configurable in the library
    
    def search(
        self,
        query: str,
        max_results: int,
        logger: logging.Logger,
        category: str
    ) -> List[str]:
        """
        Search Wikipedia with exponential backoff retry logic.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            logger: Logger instance
            category: Category name for logging
            
        Returns:
            List of Wikipedia page titles
        """
        for attempt in range(self.max_retries):
            try:
                results = wikipedia.search(query, results=max_results)
                return results
            except Exception as e:
                wait_time = 2 ** attempt
                logger.error(
                    f"Search attempt {attempt + 1} failed for query '{query}': {e}",
                    extra={'category': category}
                )
                
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"All retry attempts exhausted for query '{query}'",
                        extra={'category': category}
                    )
                    return []
        
        return []
    
    def fetch_page(
        self,
        title: str,
        logger: logging.Logger,
        category: str
    ) -> Optional[Tuple[str, str]]:
        """
        Fetch Wikipedia page content with retry logic.
        
        Args:
            title: Wikipedia page title
            logger: Logger instance
            category: Category name for logging
            
        Returns:
            Tuple of (url, content) or None if fetch fails
        """
        for attempt in range(self.max_retries):
            try:
                page = wikipedia.page(title, auto_suggest=False)
                return (page.url, page.content)
            except wikipedia.DisambiguationError as e:
                logger.warning(
                    f"Disambiguation page encountered: {title}",
                    extra={'category': category}
                )
                return None
            except wikipedia.PageError:
                logger.warning(
                    f"Page not found: {title}",
                    extra={'category': category}
                )
                return None
            except Exception as e:
                wait_time = 2 ** attempt
                logger.error(
                    f"Fetch attempt {attempt + 1} failed for '{title}': {e}",
                    extra={'category': category}
                )
                
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
        
        return None