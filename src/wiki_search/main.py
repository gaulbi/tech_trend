"""
Main entry point for wiki_search module.
"""

import argparse
import datetime
import logging
import re
import sys
from pathlib import Path
from typing import List, Optional

from .config import Config
from .exceptions import ConfigurationError
from .logger import setup_logger
from .processor import WikiSearchProcessor

logger = logging.getLogger("wiki_search")

DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Search Wikipedia and extract content for tech trends"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Specific category to process (optional)",
    )
    parser.add_argument(
        "--feed_date",
        type=str,
        help="Feed date in YYYY-MM-DD format (default: today)",
    )
    return parser.parse_args()


def validate_feed_date(feed_date: str) -> bool:
    """
    Validate feed date format.

    Args:
        feed_date: Date string to validate

    Returns:
        True if valid YYYY-MM-DD format
    """
    if not DATE_PATTERN.match(feed_date):
        return False

    try:
        parts = feed_date.split('-')
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        datetime.date(year, month, day)
        return True
    except (ValueError, IndexError):
        return False


def get_feed_date(feed_date_arg: Optional[str]) -> str:
    """
    Get feed date from argument or use today.

    Args:
        feed_date_arg: Feed date argument from command line

    Returns:
        Feed date in YYYY-MM-DD format

    Raises:
        ValueError: If feed_date_arg has invalid format
    """
    if feed_date_arg:
        if not validate_feed_date(feed_date_arg):
            raise ValueError(
                f"Invalid feed_date format: '{feed_date_arg}'. "
                f"Expected YYYY-MM-DD"
            )
        return feed_date_arg
    return datetime.date.today().strftime('%Y-%m-%d')


def get_category_files(
    config: Config,
    feed_date: str,
    category_filter: Optional[str]
) -> List[Path]:
    """
    Get list of category files to process.

    Args:
        config: Configuration object
        feed_date: Feed date
        category_filter: Optional category to filter

    Returns:
        List of category file paths
    """
    input_dir = Path(config.analysis_report_base) / feed_date

    if not input_dir.exists():
        return []

    if category_filter:
        category_file = input_dir / f"{category_filter}.json"
        return [category_file] if category_file.exists() else []

    return sorted(input_dir.glob("*.json"))


def main() -> None:
    """Main execution function."""
    args = parse_arguments()

    try:
        # Load configuration
        config = Config()

        # Get and validate feed date
        try:
            feed_date = get_feed_date(args.feed_date)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        # Setup logging
        log_dir = Path(config.log_dir)
        log_file = log_dir / f"wiki-search-{feed_date}.log"
        setup_logger(log_file)

        logger.info(f"Starting Wikipedia search for feed date: {feed_date}")

        # Get category files to process
        category_files = get_category_files(
            config,
            feed_date,
            args.category
        )

        if not category_files:
            if args.category:
                logger.warning(
                    f"No input file found for category '{args.category}' "
                    f"on {feed_date}"
                )
            else:
                logger.warning(
                    f"No input files found for feed date: {feed_date}"
                )
            sys.exit(0)

        # Process each category
        processor = WikiSearchProcessor(config)
        total = len(category_files)
        
        logger.info(f"Found {total} categories to process")
        
        for idx, category_file in enumerate(category_files, 1):
            category = category_file.stem
            logger.info(f"Processing category {idx}/{total}: {category}")
            processor.process_category(category_file, feed_date)

        logger.info(
            f"Completed processing {total} categories for {feed_date}"
        )

    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)