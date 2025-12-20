"""Command-line interface for article publisher."""

import argparse
import sys
from datetime import date
from typing import Optional

from .core import ArticlePublisher
from .config import load_config
from .logger import setup_logging, get_logger
from .exceptions import ConfigurationError


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Publish technology articles to Hashnode"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Specific category to publish"
    )
    parser.add_argument(
        "--feed_date",
        type=str,
        help="Feed date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--file_name",
        type=str,
        help="Specific article file name (requires category and feed_date)"
    )
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate command line arguments."""
    if args.file_name and (not args.category or not args.feed_date):
        raise ValueError(
            "--file_name requires both --category and --feed_date"
        )


def main() -> None:
    """Main entry point for article publisher."""
    try:
        # Parse arguments
        args = parse_arguments()
        validate_arguments(args)
        
        # Determine feed date
        feed_date = args.feed_date or date.today().strftime('%Y-%m-%d')
        
        # Load configuration
        config = load_config()
        
        # Setup logging
        log_dir = config["article-publisher"]["log"]
        setup_logging(log_dir, feed_date)
        logger = get_logger(__name__)
        
        logger.info(
            f"Starting article publisher for feed_date={feed_date}",
            extra={"feed_date": feed_date}
        )
        
        # Initialize publisher
        publisher = ArticlePublisher(config, feed_date)
        
        # Run publisher
        if args.file_name:
            # Publish specific file
            logger.info(
                f"Publishing single file: {args.file_name}",
                extra={
                    "category": args.category,
                    "file_name": args.file_name
                }
            )
            publisher.publish_single_article(
                args.category,
                args.file_name
            )
        elif args.category:
            # Publish specific category
            logger.info(
                f"Publishing category: {args.category}",
                extra={"category": args.category}
            )
            publisher.publish_category(args.category)
        else:
            # Publish all categories
            logger.info("Publishing all categories")
            publisher.publish_all()
        
        logger.info("Article publisher completed successfully")
        
    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(
            f"Fatal error: {e}",
            exc_info=True,
            extra={"error_type": type(e).__name__}
        )
        sys.exit(1)
