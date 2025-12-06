"""Orchestrator for RSS fetching process."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .config import Config
from .fetcher import FeedFetcher
from .utils import get_output_path, sanitize_category
from .validator import load_rss_list


class FetchStats:
    """Statistics for fetch operation."""
    
    def __init__(self):
        """Initialize statistics."""
        self.total_categories = 0
        self.successful_categories = 0
        self.failed_categories = 0
        self.skipped_categories = 0
        self.total_articles = 0
        self.start_time = datetime.now()
    
    def add_success(self, article_count: int) -> None:
        """Record successful category fetch."""
        self.successful_categories += 1
        self.total_articles += article_count
    
    def add_failure(self) -> None:
        """Record failed category fetch."""
        self.failed_categories += 1
    
    def add_skip(self) -> None:
        """Record skipped category."""
        self.skipped_categories += 1
    
    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    def print_summary(self) -> None:
        """Print summary statistics."""
        print("\n=== RSS Fetch Summary ===")
        print(f"Total categories: {self.total_categories}")
        print(f"Successful: {self.successful_categories}")
        print(f"Failed: {self.failed_categories}")
        print(f"Skipped: {self.skipped_categories}")
        print(f"Total articles: {self.total_articles}")
        print(f"Duration: {self.duration:.1f} seconds")


class RSSOrchestrator:
    """Orchestrates RSS fetching process."""
    
    def __init__(self, config: Config, logger: logging.Logger):
        """Initialize orchestrator.
        
        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.fetcher = FeedFetcher(
            timeout=config.timeout,
            max_retry=config.retry,
            max_concurrent=config.max_concurrent,
            logger=logger
        )
    
    def should_skip_category(
        self,
        category: str,
        feed_date: str
    ) -> bool:
        """Check if category should be skipped (already fetched).
        
        Args:
            category: Category name
            feed_date: Feed date string
            
        Returns:
            True if output file already exists
        """
        output_path = get_output_path(
            self.config.rss_feed_dir,
            feed_date,
            category
        )
        return output_path.exists()
    
    async def process_category(
        self,
        category: str,
        feeds: Dict[str, str],
        feed_date: str,
        stats: FetchStats,
        index: int,
        total: int
    ) -> None:
        """Process single category.
        
        Args:
            category: Category name
            feeds: Dictionary of feed sources
            feed_date: Feed date string
            stats: Statistics tracker
            index: Current category index (1-based)
            total: Total number of categories
        """
        if self.should_skip_category(category, feed_date):
            print(f"Skipping [{index}/{total}] categories: "
                  f"{category} (already fetched)")
            self.logger.info(
                f"Skipping category '{category}' - already fetched"
            )
            stats.add_skip()
            return
        
        print(f"Fetching [{index}/{total}] categories: {category}")
        
        try:
            successful, articles = await self.fetcher.fetch_category(
                category, feeds
            )
            
            sanitized = sanitize_category(category)
            output_path = get_output_path(
                self.config.rss_feed_dir,
                feed_date,
                category
            )
            
            self.fetcher.save_category_output(
                output_path,
                sanitized,
                feed_date,
                articles
            )
            
            if successful > 0:
                stats.add_success(len(articles))
            else:
                stats.add_failure()
        
        except Exception as e:
            self.logger.error(
                f"Failed to process category '{category}': {e}",
                exc_info=True
            )
            stats.add_failure()
    
    async def run(
        self,
        feed_date: str,
        target_category: Optional[str] = None
    ) -> FetchStats:
        """Run RSS fetching process.
        
        Args:
            feed_date: Feed date in YYYY-MM-DD format
            target_category: Specific category to fetch (None = all)
            
        Returns:
            Statistics about the fetch operation
        """
        self.logger.info(f"Starting RSS fetch for date: {feed_date}")
        
        # Load RSS list
        rss_list = load_rss_list(self.config.rss_source)
        
        # Filter categories if specified
        if target_category:
            if target_category not in rss_list:
                self.logger.error(
                    f"Category '{target_category}' not found in RSS list"
                )
                raise ValueError(
                    f"Category '{target_category}' not found"
                )
            categories = {target_category: rss_list[target_category]}
        else:
            categories = rss_list
        
        stats = FetchStats()
        stats.total_categories = len(categories)
        
        # Process categories sequentially
        for idx, (category, feeds) in enumerate(categories.items(), 1):
            await self.process_category(
                category,
                feeds,
                feed_date,
                stats,
                idx,
                len(categories)
            )
        
        self.logger.info(
            f"Completed RSS fetch: {stats.successful_categories} successful, "
            f"{stats.failed_categories} failed, "
            f"{stats.skipped_categories} skipped"
        )
        
        return stats