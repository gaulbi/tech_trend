#!/usr/bin/env python3
"""
Main entry point for the semantic deduplication system.
"""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from deduplicator.core import DeduplicationPipeline
from deduplicator.config import load_config
from deduplicator.logger import setup_logging, get_logger
from deduplicator.exceptions import ConfigurationError


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Semantic deduplication for tech trends"
    )
    parser.add_argument(
        "--feed_date",
        type=str,
        help="Feed date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Specific category to process (default: all)",
    )
    return parser.parse_args()


def main() -> int:
    """Main execution function."""
    args = parse_args()
    
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        setup_logging(config)
        logger = get_logger(__name__)
        
        logger.info("Starting deduplication pipeline")
        
        # Initialize and run pipeline
        pipeline = DeduplicationPipeline(config)
        pipeline.run(feed_date=args.feed_date, category=args.category)
        
        logger.info("Deduplication pipeline completed successfully")
        return 0
        
    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
