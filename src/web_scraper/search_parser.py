# src/web_scraper/search_parser.py
"""Parse search engine results to extract article URLs."""

import re
from typing import List
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup


class SearchParser:
    """Parse search engine HTML to extract result URLs."""
    
    @staticmethod
    def parse_google_results(html: str, max_results: int = 5) -> List[str]:
        """
        Parse Google search results HTML to extract article URLs.
        
        Args:
            html: HTML content from Google search
            max_results: Maximum number of URLs to extract
            
        Returns:
            List of extracted article URLs
        """
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            urls: List[str] = []
            
            # Find search result links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Google wraps URLs in /url?q=...
                if '/url?q=' in href:
                    parsed = urlparse(href)
                    params = parse_qs(parsed.query)
                    
                    if 'q' in params:
                        url = params['q'][0]
                        
                        # Filter out non-article URLs
                        if SearchParser._is_valid_article_url(url):
                            urls.append(url)
                            
                            if len(urls) >= max_results:
                                break
            
            return urls
            
        except Exception:
            return []
    
    @staticmethod
    def _is_valid_article_url(url: str) -> bool:
        """
        Check if URL is likely a valid article.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL appears to be a valid article
        """
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Exclude Google's own URLs
        excluded_domains = [
            'google.com',
            'youtube.com',
            'facebook.com',
            'twitter.com'
        ]
        
        parsed = urlparse(url)
        for domain in excluded_domains:
            if domain in parsed.netloc:
                return False
        
        return True