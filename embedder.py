#!/usr/bin/env python3
"""
Main entry point for the embedder module.

Processes scraped articles, chunks them, generates embeddings, and stores
them in ChromaDB with idempotency checks.
"""

import argparse
import datetime
import logging
import sys
from pathlib import Path

from src.embedder.config import load_config
from src.embedder.exceptions import ConfigurationError
from src.embedder.processor import EmbeddingProcessor
from src.embedder.utils import setup_logging

from dotenv import load_dotenv
load_dotenv(override=True)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments with date parameter.
    """
    parser = argparse.ArgumentParser(
        description="Embed scraped articles into ChromaDB"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=datetime.date.today().strftime("%Y-%m-%d"),
        help="Target date in YYYY-MM-DD format (default: today)",
    )
    return parser.parse_args()


def validate_date(date_str: str) -> str:
    """
    Validate date format.

    Args:
        date_str: Date string in YYYY-MM-DD format.

    Returns:
        Validated date string.

    Raises:
        ValueError: If date format is invalid.
    """
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError as e:
        raise ValueError(
            f"Invalid date format '{date_str}'. Expected YYYY-MM-DD"
        ) from e


def main() -> int:
    """
    Main execution function.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    args = parse_arguments()

    try:
        # Validate date
        target_date = validate_date(args.date)

        # Load configuration
        config = load_config()

        # Setup logging
        logger = setup_logging(config)
        logger.info(f"Starting embedder for date: {target_date}")

        # Initialize processor
        processor = EmbeddingProcessor(config, target_date)

        # Run processing
        result = processor.process()

        # Log summary
        logger.info(
            f"Processing complete. "
            f"Success: {result['success']}, "
            f"Skipped: {result['skipped']}, "
            f"Failed: {result['failed']}"
        )

        return 0

    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())