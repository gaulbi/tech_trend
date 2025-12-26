"""
Main orchestration module for image generation pipeline.
"""
import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Optional

from .config import ConfigManager
from .logger import setup_logger, log_function_call
from .processor import ImageProcessor
from .exceptions import ConfigurationError


@log_function_call
def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate images for technical articles"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Specific category to process"
    )
    parser.add_argument(
        "--feed_date",
        type=str,
        help="Feed date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--file_name",
        type=str,
        help="Specific markdown file to process (requires category and feed_date)"
    )
    return parser.parse_args()


@log_function_call
def validate_arguments(args: argparse.Namespace) -> None:
    """Validate command line argument combinations."""
    if args.file_name and (not args.category or not args.feed_date):
        raise ValueError(
            "file_name requires both category and feed_date to be specified"
        )


@log_function_call
def determine_feed_date(feed_date_arg: Optional[str]) -> str:
    """Determine the feed date to use."""
    if feed_date_arg:
        return feed_date_arg
    return date.today().strftime('%Y-%m-%d')


def main() -> int:
    """Main entry point for the image generator."""
    try:
        args = parse_arguments()
        validate_arguments(args)
        
        feed_date = determine_feed_date(args.feed_date)
        
        config = ConfigManager()
        logger = setup_logger(config, feed_date)
        
        logger.info(
            "Starting image generation",
            extra={
                "feed_date": feed_date,
                "category": args.category,
                "file_name": args.file_name
            }
        )
        
        processor = ImageProcessor(config, logger, feed_date)
        processor.process(
            category=args.category,
            file_name=args.file_name
        )
        
        logger.info("Image generation completed successfully")
        return 0
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Invalid arguments: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
