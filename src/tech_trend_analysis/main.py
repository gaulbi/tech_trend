# ============================================================================
# src/tech_trend_analysis/main.py
# ============================================================================

"""Main application logic and CLI entry point."""

import argparse
import sys
from datetime import date
from pathlib import Path

from .config import Config
from .exceptions import ConfigurationError, TechTrendAnalysisError
from .llm.factory import LLMClientFactory
from .processor import TechTrendProcessor
from .utils.file_ops import read_text_file, list_json_files
from .utils.logger import setup_logger


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Tech Trend Analysis - Generate daily trend reports'
    )
    parser.add_argument(
        '--category',
        type=str,
        help='Specific category to process (e.g., software_engineering)'
    )
    parser.add_argument(
        '--feed_date',
        type=str,
        help='Feed date to process (YYYY-MM-DD format)'
    )
    return parser.parse_args()


def get_feed_date(args: argparse.Namespace) -> str:
    """
    Determine feed date from arguments or use today's date.

    Args:
        args: Parsed command line arguments

    Returns:
        Feed date string in YYYY-MM-DD format
    """
    if args.feed_date:
        return args.feed_date
    return date.today().strftime('%Y-%m-%d')


def get_category_files(
    config: Config,
    feed_date: str,
    category_filter: str = None
) -> list:
    """
    Get list of category files to process.

    Args:
        config: Application configuration
        feed_date: Feed date string
        category_filter: Optional category name filter

    Returns:
        List of category file paths
    """
    rss_dir = Path(config.rss_feed_path) / feed_date

    if not rss_dir.exists():
        return []

    all_files = list_json_files(rss_dir)

    if category_filter:
        # Filter for specific category
        filtered = [
            f for f in all_files
            if f.stem == category_filter
        ]
        return filtered

    return all_files


def main() -> None:
    """Main entry point for the application."""
    try:
        # Parse arguments
        args = parse_args()
        feed_date = get_feed_date(args)

        # Load configuration
        config = Config()

        # Setup logger
        log_file = Path(config.log_path) / f"tech-trend-analysis-{feed_date}.log"
        logger = setup_logger(
            'tech_trend_analysis',
            log_file=str(log_file),
            json_format=True
        )

        logger.info(f"Starting tech trend analysis for {feed_date}")

        # Create LLM client
        llm_client = LLMClientFactory.create(config)
        logger.info(f"Using LLM provider: {config.llm_server}")

        # Load prompt template
        prompt_path = Path(config.prompt_path)
        prompt_template = read_text_file(prompt_path)

        # Get category files to process
        category_files = get_category_files(
            config,
            feed_date,
            args.category
        )

        if not category_files:
            if args.category:
                logger.warning(
                    f"No RSS feed found for category '{args.category}' "
                    f"on {feed_date}"
                )
            else:
                logger.warning(
                    f"No RSS feeds found for {feed_date}"
                )
            return

        logger.info(f"Found {len(category_files)} categories to process")

        # Process each category
        processor = TechTrendProcessor(config, llm_client, logger)
        success_count = 0
        fail_count = 0

        for category_file in category_files:
            logger.info(f"Processing {category_file.stem}...")

            if processor.process_category(
                category_file,
                feed_date,
                prompt_template
            ):
                success_count += 1
            else:
                fail_count += 1

        # Summary
        logger.info(
            f"Processing complete: {success_count} succeeded, "
            f"{fail_count} failed"
        )

        if fail_count > 0:
            sys.exit(1)

    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)

    except TechTrendAnalysisError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)