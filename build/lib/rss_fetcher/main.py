"""Main orchestration for RSS fetcher."""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

from .config_loader import load_config, load_rss_list
from .logger import setup_logger
from .rss_fetcher import RssFetcher
from .models import Article, CategoryOutput
from .utils import sanitize_category_name, is_today_file_exists, get_output_path


class RssFetcherOrchestrator:
    """Main orchestrator for RSS fetching workflow."""
    
    def __init__(self):
        """Initialize orchestrator with configuration."""
        self.config = load_config()
        self.logger = setup_logger(self.config.rss.log)
        self.rss_list = load_rss_list(self.config.rss.rss_list)
        self.fetcher = RssFetcher(
            timeout=self.config.rss.timeout,
            max_retries=self.config.rss.retry,
            logger=self.logger
        )
        
        self.stats = {
            'total': len(self.rss_list),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_articles': 0
        }
    
    def _save_category_output(
        self,
        category: str,
        sanitized_category: str,
        articles: list
    ) -> None:
        """
        Save category output to JSON file.
        
        Args:
            category: Original category name
            sanitized_category: Sanitized category name
            articles: List of article dictionaries
        """
        output = CategoryOutput(
            category=sanitized_category,
            fetch_date=datetime.now().strftime("%Y-%m-%d"),
            article_count=len(articles),
            articles=[Article(**article) for article in articles]
        )
        
        output_path = get_output_path(
            self.config.rss.rss_feed,
            sanitized_category
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output.model_dump(), f, indent=2, ensure_ascii=False)
        
        self.logger.info(
            f"Saved {len(articles)} articles for category '{category}'",
            extra={
                'category': category,
                'status': 'success'
            }
        )
    
    async def _process_category(
        self,
        index: int,
        category: str,
        feeds: Dict[str, str]
    ) -> None:
        """
        Process a single category.
        
        Args:
            index: Category index (1-based)
            category: Category name
            feeds: Dictionary of feed sources
        """
        sanitized = sanitize_category_name(category)
        
        if is_today_file_exists(self.config.rss.rss_feed, sanitized):
            print(
                f"Skipping [{index}/{self.stats['total']}] categories: "
                f"{category} (already fetched)"
            )
            self.logger.info(
                f"Skipping category '{category}' (already fetched today)",
                extra={
                    'category': category,
                    'status': 'skipped'
                }
            )
            self.stats['skipped'] += 1
            return
        
        print(f"Fetching [{index}/{self.stats['total']}] categories: {category}")
        
        self.logger.info(
            f"Starting fetch for category '{category}'",
            extra={'category': category}
        )
        
        try:
            articles = await self.fetcher.fetch_category(
                category,
                feeds,
                self.config.rss.max_concurrent
            )
            
            self._save_category_output(category, sanitized, articles)
            
            self.stats['successful'] += 1
            self.stats['total_articles'] += len(articles)
            
        except Exception as e:
            self.logger.error(
                f"Failed to process category '{category}': {str(e)}",
                extra={
                    'category': category,
                    'status': 'failure',
                    'error_message': str(e)
                }
            )
            self.stats['failed'] += 1
            
            self._save_category_output(category, sanitized, [])
    
    async def run(self) -> None:
        """Execute the RSS fetching workflow."""
        start_time = time.time()
        
        self.logger.info("Starting RSS fetch process")
        
        if not self.rss_list:
            print("No categories to fetch")
            self.logger.info("No categories found in RSS list")
            self._print_summary(0)
            return
        
        try:
            for index, (category, feeds) in enumerate(self.rss_list.items(), 1):
                await self._process_category(index, category, feeds)
            
            duration = time.time() - start_time
            self._print_summary(duration)
            
            self.logger.info(
                "RSS fetch process completed",
                extra={'status': 'success'}
            )
        finally:
            self.fetcher.executor.shutdown(wait=True)
    
    def _print_summary(self, duration: float) -> None:
        """
        Print execution summary to stdout.
        
        Args:
            duration: Execution duration in seconds
        """
        print("\n=== RSS Fetch Summary ===")
        print(f"Total categories: {self.stats['total']}")
        print(f"Successful: {self.stats['successful']}")
        
        if self.stats['skipped'] > 0:
            print(f"Skipped: {self.stats['skipped']}")
        
        if self.stats['failed'] > 0:
            print(f"Failed: {self.stats['failed']}")
        
        print(f"Total articles: {self.stats['total_articles']}")
        print(f"Duration: {duration:.1f} seconds")


def main() -> None:
    """Entry point for RSS fetcher."""
    try:
        orchestrator = RssFetcherOrchestrator()
        asyncio.run(orchestrator.run())
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        raise