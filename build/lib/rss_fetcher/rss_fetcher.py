"""Async RSS fetching with retry logic and rate limiting."""

import asyncio
import feedparser
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import aiohttp


class RateLimiter:
    """Rate limiter to control requests per domain."""
    
    def __init__(self, max_per_second: float = 2.0):
        """
        Initialize rate limiter.
        
        Args:
            max_per_second: Maximum requests per second per domain
        """
        self.max_per_second = max_per_second
        self.domain_locks: Dict[str, asyncio.Lock] = {}
        self.last_request: Dict[str, float] = {}
        self._lock_creation_lock = asyncio.Lock()
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        return urlparse(url).netloc
    
    async def acquire(self, url: str) -> None:
        """
        Acquire rate limit token for URL's domain.
        
        Args:
            url: URL to rate limit
        """
        domain = self._get_domain(url)
        
        async with self._lock_creation_lock:
            if domain not in self.domain_locks:
                self.domain_locks[domain] = asyncio.Lock()
        
        async with self.domain_locks[domain]:
            if domain in self.last_request:
                elapsed = time.time() - self.last_request[domain]
                min_interval = 1.0 / self.max_per_second
                
                if elapsed < min_interval:
                    await asyncio.sleep(min_interval - elapsed)
            
            self.last_request[domain] = time.time()


class RssFetcher:
    """Async RSS feed fetcher with retry and rate limiting."""
    
    def __init__(
        self,
        timeout: int,
        max_retries: int,
        logger: logging.Logger
    ):
        """
        Initialize RSS fetcher.
        
        Args:
            timeout: HTTP timeout in seconds
            max_retries: Maximum retry attempts
            logger: Logger instance
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger
        self.rate_limiter = RateLimiter(max_per_second=2.0)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def _parse_feed(self, content: str) -> feedparser.FeedParserDict:
        """
        Parse RSS feed content synchronously.
        
        Args:
            content: Raw RSS feed content
            
        Returns:
            Parsed feed object
        """
        return feedparser.parse(content)
    
    async def fetch_feed(
        self,
        session: aiohttp.ClientSession,
        feed_name: str,
        feed_url: str,
        category: str
    ) -> Optional[List[Dict[str, str]]]:
        """
        Fetch and parse a single RSS feed with retry logic.
        
        Args:
            session: aiohttp session
            feed_name: Name of the feed source
            feed_url: URL of the RSS feed
            category: Category name for logging
            
        Returns:
            List of articles or None on failure
        """
        for attempt in range(self.max_retries):
            try:
                await self.rate_limiter.acquire(feed_url)
                
                async with session.get(
                    feed_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    content = await response.text()
                    articles = await self._parse_rss_content(
                        content, feed_name, feed_url, category
                    )
                    return articles
                    
            except asyncio.TimeoutError:
                await self._handle_retry(
                    attempt, feed_name, feed_url, category, "Timeout"
                )
                    
            except Exception as e:
                await self._handle_retry(
                    attempt, feed_name, feed_url, category, str(e)
                )
        
        return None
    
    async def _parse_rss_content(
        self,
        content: str,
        feed_name: str,
        feed_url: str,
        category: str
    ) -> List[Dict[str, str]]:
        """Parse RSS content and extract articles."""
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(
            self.executor,
            self._parse_feed,
            content
        )
        
        if feed.bozo and not feed.entries:
            raise Exception(f"Invalid RSS: {feed.bozo_exception}")
        
        articles = []
        for entry in feed.entries:
            title = getattr(entry, 'title', '').strip()
            link = getattr(entry, 'link', '').strip()
            
            if title and link:
                articles.append({'title': title, 'link': link})
        
        self.logger.info(
            f"Fetched {len(articles)} articles from {feed_name}",
            extra={
                'category': category,
                'feed_url': feed_url,
                'status': 'success'
            }
        )
        return articles
    
    async def _handle_retry(
        self,
        attempt: int,
        feed_name: str,
        feed_url: str,
        category: str,
        error_msg: str
    ) -> None:
        """Handle retry logic with exponential backoff."""
        wait_time = 2 ** attempt
        self.logger.error(
            f"Error fetching {feed_name} (attempt {attempt + 1}): {error_msg}",
            extra={
                'category': category,
                'feed_url': feed_url,
                'status': 'failure',
                'error_message': error_msg
            }
        )
        if attempt < self.max_retries - 1:
            await asyncio.sleep(wait_time)
    
    async def fetch_category(
        self,
        category: str,
        feeds: Dict[str, str],
        max_concurrent: int
    ) -> List[Dict[str, str]]:
        """
        Fetch all feeds for a category with concurrency control.
        
        Args:
            category: Category name
            feeds: Dictionary mapping feed names to URLs
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of all articles from category (deduplicated)
        """
        if not feeds:
            self.logger.info(
                f"No feeds configured for category '{category}'",
                extra={'category': category}
            )
            return []
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(
            session: aiohttp.ClientSession,
            name: str,
            url: str
        ):
            async with semaphore:
                return await self.fetch_feed(session, name, url, category)
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                fetch_with_semaphore(session, name, url)
                for name, url in feeds.items()
            ]
            results = await asyncio.gather(*tasks)
        
        all_articles = []
        seen_links = set()
        
        for articles in results:
            if articles:
                for article in articles:
                    link = article['link']
                    if link not in seen_links:
                        seen_links.add(link)
                        all_articles.append(article)
                    else:
                        self.logger.debug(
                            f"Skipping duplicate article: {article['title']}",
                            extra={'category': category}
                        )
        
        return all_articles