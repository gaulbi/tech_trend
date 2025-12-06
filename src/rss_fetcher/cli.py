"""Command-line interface for RSS fetcher."""

import argparse
import asyncio
import sys
from datetime import date
from pathlib import Path

from .config import Config, ConfigurationError
from .logger import setup_logger
from .orchestrator import RSSOrchestrator
from .validator import ValidationError


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Fetch RSS feeds and save to JSON files'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Specific category to fetch (default: fetch all)'
    )
    
    parser.add_argument(
        '--feed_date',
        type=str,
        help='Feed date in YYYY-MM-DD format (default: today)'
    )
    
    return parser.parse_args()


def get_feed_date(date_str: str = None) -> str:
    """Get feed date from argument or use today.
    
    Args:
        date_str: Optional date string in YYYY-MM-DD format
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    if date_str:
        return date_str
    return date.today().strftime('%Y-%m-%d')


def main() -> int:
    """Main entry point for RSS fetcher.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        feed_date = get_feed_date(args.feed_date)
        
        # Load configuration
        config = Config()
        
        # Setup logger
        log_dir = Path(config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"rss-fetcher-{feed_date}.log"
        
        logger = setup_logger(
            name='rss_fetcher',
            log_file=str(log_file),
            json_format=True
        )
        
        logger.info("=" * 60)
        logger.info("RSS Fetcher started")
        logger.info(f"Feed date: {feed_date}")
        if args.category:
            logger.info(f"Target category: {args.category}")
        logger.info("=" * 60)
        
        # Run orchestrator
        orchestrator = RSSOrchestrator(config, logger)
        stats = asyncio.run(
            orchestrator.run(feed_date, args.category)
        )
        
        # Print summary
        stats.print_summary()
        
        logger.info("RSS Fetcher completed successfully")
        return 0
    
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    
    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())