"""Command-line interface for RSS Fetcher."""

import sys
import logging
from pathlib import Path
from typing import Optional

from .config import Config
from .sources import RSSSourcesLoader
from .fetcher import RSSFetcher
from .writer import OutputWriter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class RSSFetcherCLI:
    """Command-line interface for RSS fetcher."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize CLI with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            self.config = Config(config_path)
            self.sources_loader = RSSSourcesLoader(self.config.rss_list_path)
            self.fetcher = RSSFetcher()
            self.writer = OutputWriter(self.config.rss_feed_dir)
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
    
    def run(self) -> int:
        """
        Execute RSS fetching for all categories.
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        categories = self.sources_loader.get_categories()
        
        if not categories:
            logger.warning("No categories found in sources file")
            return 0
        
        logger.info(f"Starting RSS fetch for {len(categories)} categories")
        print(f"\n{'='*60}")
        print(f"RSS Fetcher - Processing {len(categories)} categories")
        print(f"{'='*60}\n")
        
        total_articles = 0
        successful_categories = 0
        failed_categories = 0
        
        for i, category in enumerate(categories, 1):
            try:
                print(f"[{i}/{len(categories)}] Processing: {category}")
                
                # Get sources for category
                sources = self.sources_loader.get_sources_for_category(category)
                
                if not sources:
                    logger.warning(f"No sources found for category: {category}")
                    print(f"  ⚠️  No sources configured")
                    continue
                
                print(f"  📡 Fetching from {len(sources)} source(s)...")
                
                # Fetch feeds
                category_data = self.fetcher.fetch_category(sources, category)
                
                # Write to file
                category_filename = RSSSourcesLoader.category_to_filename(category)
                output_path = self.writer.write_category(category_data, category_filename)
                
                article_count = category_data['article_count']
                total_articles += article_count
                successful_categories += 1
                
                print(f"  ✅ Saved {article_count} articles to {output_path.name}")
                print()
                
            except Exception as e:
                failed_categories += 1
                logger.error(f"Failed to process category {category}: {e}")
                print(f"  ❌ Error: {e}")
                print()
        
        # Print summary
        print(f"{'='*60}")
        print("Summary:")
        print(f"  Total categories: {len(categories)}")
        print(f"  Successful: {successful_categories}")
        print(f"  Failed: {failed_categories}")
        print(f"  Total articles fetched: {total_articles}")
        print(f"  Output directory: {self.config.rss_feed_dir}")
        print(f"{'='*60}\n")
        
        return 0 if failed_categories == 0 else 1


def main() -> None:
    """Main entry point for CLI."""
    try:
        cli = RSSFetcherCLI()
        exit_code = cli.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)