# src/web_scraper/scraper.py
"""Core scraping logic."""

import logging
from typing import List, Optional
from urllib.parse import quote_plus

from .models import Trend, ScrapedTrend
from .scraper_clients import BaseScraperClient
from .search_parser import SearchParser
from .content_cleaner import ContentCleaner


class WebScraper:
    """Handles web scraping operations."""
    
    GOOGLE_SEARCH_URL = "https://www.google.com/search?q={}"
    
    def __init__(
        self,
        client: BaseScraperClient,
        max_results: int,
        logger: logging.Logger
    ):
        """
        Initialize web scraper.
        
        Args:
            client: Scraper API client
            max_results: Maximum search results to scrape per query
            logger: Logger instance
        """
        self.client = client
        self.max_results = max_results
        self.logger = logger
        self.parser = SearchParser()
        self.cleaner = ContentCleaner()
    
    def scrape_trend(self, trend: Trend) -> List[ScrapedTrend]:
        """
        Scrape content for a single trend.
        
        Args:
            trend: Trend object with search keywords
            
        Returns:
            List of scraped trend objects
        """
        results: List[ScrapedTrend] = []
        
        for query in trend.search_keywords:
            self.logger.info(f"Processing query: {query}")
            
            # Search phase
            article_urls = self._search(query)
            
            if not article_urls:
                self.logger.warning(f"No results found for query: {query}")
                continue
            
            # Scrape phase
            for url in article_urls:
                scraped = self._scrape_article(trend.topic, query, url)
                if scraped:
                    results.append(scraped)
        
        return results
    
    def _search(self, query: str) -> List[str]:
        """
        Search for articles using query.
        
        Args:
            query: Search query string
            
        Returns:
            List of article URLs
        """
        search_url = self.GOOGLE_SEARCH_URL.format(quote_plus(query))
        
        html = self.client.fetch(search_url)
        if not html:
            self.logger.error(f"Failed to fetch search results for: {query}")
            return []
        
        urls = self.parser.parse_google_results(html, self.max_results)
        self.logger.info(f"Found {len(urls)} URLs for query: {query}")
        
        return urls
    
    def _scrape_article(
        self,
        topic: str,
        query: str,
        url: str
    ) -> Optional[ScrapedTrend]:
        """
        Scrape and clean content from article URL.
        
        Args:
            topic: Topic name
            query: Query that found this URL
            url: Article URL to scrape
            
        Returns:
            ScrapedTrend object or None if scraping failed
        """
        self.logger.info(f"Scraping article: {url}")
        
        # Fetch article
        html = self.client.fetch(url)
        if not html:
            self.logger.error(f"Failed to fetch article: {url}")
            return None
        
        # Clean content
        content = self.cleaner.clean(html)
        if not content:
            self.logger.warning(f"Failed to extract content from: {url}")
            return None
        
        return ScrapedTrend(
            topic=topic,
            query_used=query,
            link=url,
            content=content,
            source_search_terms=query.split()
        )