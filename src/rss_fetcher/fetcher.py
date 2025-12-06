"""Core RSS fetching functionality."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import aiohttp
import feedparser

from .utils import get_output_path, ensure_directory
from .validator import validate_article


class FeedFetcher:
    """Asynchronous RSS feed fetcher."""
    
    def __init__(
        self,
        timeout: int,
        max_retry: int,
        max_concurrent: int,
        logger: logging.Logger
    ):
        """Initialize feed fetcher.
        
        Args:
            timeout: HTTP timeout in seconds
            max_retry: Maximum retry attempts
            max_concurrent: Maximum concurrent requests
            logger: Logger instance
        """
        self.timeout = timeout
        self.max_retry = max_retry
        self.max_concurrent = max_concurrent
        self.logger = logger
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_feed(
        self,
        session: aiohttp.ClientSession,
        url: str,
        source_name: str
    ) -> Optional[List[Dict]]:
        """Fetch single RSS feed with retry logic.
        
        Args:
            session: aiohttp session
            url: Feed URL
            source_name: Name of feed source
            
        Returns:
            List of articles or None if fetch failed
        """
        async with self.semaphore:
            for attempt in range(1, self.max_retry + 1):
                try:
                    async with session.get(
                        url, 
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        if feed.bozo and not feed.entries:
                            self.logger.error(
                                f"Invalid RSS feed from {source_name}: "
                                f"{url}"
                            )
                            return None
                        
                        articles = []
                        for entry in feed.entries:
                            article = {
                                'title': entry.get('title', ''),
                                'link': entry.get('link', '')
                            }
                            
                            if validate_article(article):
                                articles.append(article)
                            else:
                                self.logger.debug(
                                    f"Skipping article missing title/link "
                                    f"from {source_name}"
                                )
                        
                        self.logger.info(
                            f"Fetched {len(articles)} articles from "
                            f"{source_name}"
                        )
                        return articles
                
                except asyncio.TimeoutError:
                    backoff = 2 ** (attempt - 1)
                    self.logger.warning(
                        f"Timeout fetching {source_name} (attempt "
                        f"{attempt}/{self.max_retry})"
                    )
                    if attempt < self.max_retry:
                        await asyncio.sleep(backoff)
                    else:
                        self.logger.error(
                            f"Max retries reached for {source_name}: {url}"
                        )
                        return None
                
                except Exception as e:
                    backoff = 2 ** (attempt - 1)
                    self.logger.warning(
                        f"Error fetching {source_name}: {e} (attempt "
                        f"{attempt}/{self.max_retry})"
                    )
                    if attempt < self.max_retry:
                        await asyncio.sleep(backoff)
                    else:
                        self.logger.error(
                            f"Failed to fetch {source_name} after "
                            f"{self.max_retry} attempts: {e}"
                        )
                        return None
    
    async def fetch_category(
        self,
        category: str,
        feeds: Dict[str, str]
    ) -> Tuple[int, List[Dict]]:
        """Fetch all feeds for a category.
        
        Args:
            category: Category name
            feeds: Dictionary of source names to URLs
            
        Returns:
            Tuple of (successful_count, all_articles)
        """
        self.logger.info(f"Fetching category: {category}")
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_feed(session, url, source)
                for source, url in feeds.items()
            ]
            results = await asyncio.gather(*tasks)
        
        # Combine results and deduplicate
        all_articles = []
        seen_links: Set[str] = set()
        successful = 0
        
        for articles in results:
            if articles is not None:
                successful += 1
                for article in articles:
                    link = article['link']
                    if link not in seen_links:
                        seen_links.add(link)
                        all_articles.append(article)
                    else:
                        self.logger.debug(
                            f"Skipping duplicate article: {link}"
                        )
        
        self.logger.info(
            f"Category '{category}': {successful}/{len(feeds)} sources "
            f"successful, {len(all_articles)} unique articles"
        )
        
        return successful, all_articles
    
    def save_category_output(
        self,
        output_path: Path,
        category: str,
        feed_date: str,
        articles: List[Dict]
    ) -> None:
        """Save category articles to JSON file.
        
        Args:
            output_path: Output file path
            category: Sanitized category name
            feed_date: Feed date string
            articles: List of articles
        """
        ensure_directory(output_path)
        
        output_data = {
            'category': category,
            'feed_date': feed_date,
            'article_count': len(articles),
            'articles': articles
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(
            f"Saved {len(articles)} articles to {output_path}"
        )