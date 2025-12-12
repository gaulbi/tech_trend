"""
Command-line interface for image generator.
"""
import argparse
import sys
from datetime import date
from pathlib import Path

from .config import load_config
from .logger import Logger
from .processor import ImageProcessor
from .exceptions import ConfigurationError


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate AI-powered images for technical articles'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Process specific category only'
    )
    
    parser.add_argument(
        '--feed_date',
        type=str,
        help='Feed date (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--file_name',
        type=str,
        help='Process specific file (requires category and feed_date)'
    )
    
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments.
    
    Args:
        args: Parsed arguments
        
    Raises:
        ValueError: If arguments are invalid
    """
    if args.file_name:
        if not args.category or not args.feed_date:
            raise ValueError(
                "Both --category and --feed_date are required "
                "when using --file_name"
            )
        if not args.file_name.endswith('.md'):
            raise ValueError(
                "file_name must end with .md extension"
            )


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        validate_arguments(args)
        
        # Load configuration
        config = load_config()
        
        # Determine feed date
        feed_date = args.feed_date or date.today().strftime('%Y-%m-%d')
        
        # Setup logger
        log_file = (
            config.image_generator.log /
            f"image-generator-{feed_date}.log"
        )
        logger = Logger(
            name="image_generator",
            log_file=log_file,
            level="DEBUG",
            use_json=True,
            retention_days=30
        )
        
        logger.info(
            f"Starting image generation for feed date: {feed_date}"
        )
        
        if args.category:
            logger.info(f"Processing category: {args.category}")
        if args.file_name:
            logger.info(f"Processing file: {args.file_name}")
        
        # Create processor
        processor = ImageProcessor(config, logger)
        
        # Process files
        stats = processor.process_batch(
            feed_date=feed_date,
            category=args.category,
            file_name=args.file_name
        )
        
        # Print summary
        print("\n" + "="*60)
        print("Image Generation Summary")
        print("="*60)
        print(f"Total files:     {stats['total']}")
        print(f"Processed:       {stats['processed']}")
        print(f"Skipped:         {stats['skipped']}")
        print(f"Failed:          {stats['failed']}")
        print("="*60)
        
        logger.info(
            f"Completed: {stats['processed']} processed, "
            f"{stats['skipped']} skipped, {stats['failed']} failed"
        )
        
        # Exit with appropriate code
        if stats['total'] == 0:
            logger.warning("No files to process")
            return 0
        
        if stats['failed'] > 0:
            logger.warning(f"{stats['failed']} files failed to process")
        
        return 0
        
    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
        
    except ValueError as e:
        print(f"Argument Error: {e}", file=sys.stderr)
        return 1
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
