"""
Main module for URL scraper application.
"""

import argparse
import datetime
from pathlib import Path
from typing import Optional

from .config import Config, ConfigurationError
from .logger import get_logger, setup_logging
from .processor import URLScraperProcessor


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Scrape URLs from tech trend analysis reports"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Specific category to process (optional)"
    )
    parser.add_argument(
        "--feed_date",
        type=str,
        help="Feed date in YYYY-MM-DD format (default: today)"
    )
    return parser.parse_args()


def validate_feed_date(feed_date_str: str) -> str:
    """
    Validate feed date format.
    
    Args:
        feed_date_str: Date string in YYYY-MM-DD format.
        
    Returns:
        Validated date string.
        
    Raises:
        ValueError: If date format is invalid.
    """
    try:
        datetime.datetime.strptime(feed_date_str, "%Y-%m-%d")
        return feed_date_str
    except ValueError:
        raise ValueError(
            f"Invalid date format: {feed_date_str}. "
            f"Expected YYYY-MM-DD"
        )


def main() -> int:
    """
    Main entry point for URL scraper.
    
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    args = parse_arguments()
    logger = None
    
    # Determine feed date
    if args.feed_date:
        try:
            feed_date = validate_feed_date(args.feed_date)
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    else:
        feed_date = datetime.date.today().strftime("%Y-%m-%d")
    
    try:
        # Load configuration
        config = Config.load("config.yaml")
        
        # Setup logging
        log_dir = Path(config.scrape_log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        setup_logging(log_dir, feed_date)
        
        logger = get_logger(__name__)
        logger.info(
            f"Starting URL scraper for feed_date={feed_date}, "
            f"category={args.category or 'all'}"
        )
        
        # Initialize processor
        processor = URLScraperProcessor(config, feed_date)
        
        # Process categories
        processor.process(args.category)
        
        logger.info("URL scraper completed successfully")
        return 0
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        return 1
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        else:
            print(f"Unexpected error: {e}")
        return 1