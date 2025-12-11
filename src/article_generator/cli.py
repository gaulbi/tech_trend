"""Command-line interface with comprehensive validation."""
import argparse
from datetime import date
from pathlib import Path
from .config import Config
from .logger import Logger
from .processor import ArticleProcessor
from .exceptions import ConfigurationError
from .validators import InputValidator, ValidationError


def parse_args() -> argparse.Namespace:
    """
    Parse and validate command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate technology trend articles using LLMs and RAG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --category software_engineering
  %(prog)s --feed_date 2025-02-01
  %(prog)s --cnt 5 --overwrite
  %(prog)s --category ai --feed_date 2025-02-01 --cnt 3
        """
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Specific category to process (alphanumeric, underscore, hyphen)'
    )
    
    parser.add_argument(
        '--feed_date',
        type=str,
        help='Feed date in YYYY-MM-DD format (default: today)'
    )
    
    parser.add_argument(
        '--cnt',
        type=int,
        help='Number of top trends to process (sorted by score, must be > 0)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing articles'
    )
    
    args = parser.parse_args()
    
    # Validate cnt if provided
    if args.cnt is not None and args.cnt <= 0:
        parser.error("--cnt must be greater than 0")
    
    return args


def main() -> int:
    """
    Main entry point with comprehensive error handling.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = parse_args()
    
    # Determine and validate feed date
    if args.feed_date:
        feed_date = args.feed_date
        try:
            InputValidator.validate_feed_date(feed_date)
        except ValidationError as e:
            print(f"Invalid feed_date: {str(e)}")
            return 1
    else:
        feed_date = date.today().strftime('%Y-%m-%d')
    
    # Validate category if provided
    if args.category:
        try:
            InputValidator.validate_category(args.category)
        except ValidationError as e:
            print(f"Invalid category: {str(e)}")
            return 1
    
    try:
        # Load configuration
        config = Config('config.yaml')
        
        # Initialize logger
        log_dir = Path(config.get('article-generator.log'))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"article-generator-{feed_date}.log"
        
        logger = Logger('article-generator', str(log_file))
        
        logger.info("=" * 60)
        logger.info("Article Generator Started")
        logger.info(f"Feed Date: {feed_date}")
        logger.info(f"Category: {args.category or 'ALL'}")
        logger.info(f"Count: {args.cnt or 'ALL'}")
        logger.info(f"Overwrite: {args.overwrite}")
        logger.info("=" * 60)
        
        # Initialize processor
        processor = ArticleProcessor(config, logger)
        
        # Determine categories to process
        if args.category:
            categories = [args.category]
        else:
            categories = processor.discover_categories(feed_date)
        
        if not categories:
            logger.warning("No categories found to process")
            return 0
        
        logger.info(f"Found {len(categories)} categories: {categories}")
        
        # Process each category
        total_articles = 0
        for category in categories:
            articles = processor.process_category(
                category=category,
                feed_date=feed_date,
                cnt=args.cnt,
                overwrite=args.overwrite
            )
            total_articles += articles
        
        logger.info("=" * 60)
        logger.info(f"Article Generator Completed")
        logger.info(f"Total Articles Generated: {total_articles}")
        logger.info("=" * 60)
        
        return 0
    
    except ConfigurationError as e:
        print(f"Configuration Error: {str(e)}")
        return 1
    
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1