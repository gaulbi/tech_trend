#!/usr/bin/env python3
"""
Scraped Content Embedder - Main Entry Point

This module embeds today's scraped content into ChromaDB using various embedding providers.
Supports OpenAI, Voyage AI, Gemini, and local Sentence Transformers.

Usage:
    python scrapped_content_embedder.py

Requirements:
    - config.yaml: Configuration file with paths and settings
    - .env: API keys for embedding providers (if not using local)
    - data/scraped-content/{YYYY-MM-DD}/: Today's scraped content
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from src.scrapped_content_embedder.config import Config
from src.scrapped_content_embedder.embedder import ScrapedContentEmbedder


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging with structured output to console and file.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                log_dir / f'embedder_{datetime.now().strftime("%Y%m%d")}.log'
            )
        ]
    )
    
    # Reduce verbosity of third-party libraries
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def print_summary(results: Dict[str, Any]) -> None:
    """
    Print comprehensive processing summary report.
    
    Args:
        results: Processing results dictionary from embedder
    """
    print("\n" + "="*80)
    print("EMBEDDING PROCESSING SUMMARY")
    print("="*80)
    print(f"\n📅 Execution Date: {results['execution_date']}")
    print(f"📁 Total Files Processed: {results['total_files']}")
    print(f"   ✓ Successful: {results['successful_files']}")
    print(f"   ✗ Failed: {results['failed_files']}")
    
    print(f"\n📊 Embedding Statistics:")
    print(f"   Total Chunks Created: {results['total_chunks']}")
    print(f"   Total Documents Embedded: {results['total_documents']}")
    print(f"   Successful Embeddings: {results['successful_embeddings']}")
    print(f"   Failed Embeddings: {results['failed_embeddings']}")
    
    if results['categories_processed']:
        print(f"\n📚 Categories Processed ({len(results['categories_processed'])}):")
        for category, count in sorted(results['categories_processed'].items()):
            print(f"   • {category}: {count} documents")
    else:
        print("\n⚠️  No categories were successfully processed")
    
    if results['errors']:
        print(f"\n❌ Errors Encountered ({len(results['errors'])}):")
        for idx, error in enumerate(results['errors'][:10], 1):  # Show first 10
            print(f"   {idx}. {error}")
        if len(results['errors']) > 10:
            print(f"   ... and {len(results['errors']) - 10} more errors")
    else:
        print("\n✅ No errors encountered")
    
    # Summary status
    print("\n" + "="*80)
    if results['failed_embeddings'] == 0 and results['total_documents'] > 0:
        print("STATUS: ✅ COMPLETED SUCCESSFULLY")
    elif results['total_documents'] > 0:
        print(f"STATUS: ⚠️  COMPLETED WITH {results['failed_embeddings']} FAILURES")
    else:
        print("STATUS: ❌ FAILED - No documents embedded")
    print("="*80 + "\n")


def validate_environment() -> None:
    """
    Validate that the required files and directories exist.
    
    Raises:
        FileNotFoundError: If config.yaml is missing
    """
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(
            "config.yaml not found. Please create configuration file. "
            "See config.yaml.example for reference."
        )
    
    env_path = Path(".env")
    if not env_path.exists():
        logging.warning(
            ".env file not found. Ensure you're using a provider that doesn't "
            "require API keys (e.g., sentence-transformers) or create .env file."
        )


def main() -> int:
    """
    Main execution function.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("="*80)
        logger.info("SCRAPED CONTENT EMBEDDER")
        logger.info("="*80)
        
        # Validate environment
        validate_environment()
        
        # Load configuration
        logger.info("Loading configuration from config.yaml...")
        config = Config.from_yaml("config.yaml")
        logger.info(
            f"Configuration loaded successfully\n"
            f"  Provider: {config.embedding.embedding_provider}\n"
            f"  Model: {config.embedding.embedding_model}\n"
            f"  Chunk Size: {config.embedding.chunk_size}\n"
            f"  Chunk Overlap: {config.embedding.chunk_overlap}"
        )
        
        # Initialize embedder
        logger.info("Initializing embedder...")
        embedder = ScrapedContentEmbedder(config)
        logger.info("Embedder initialized successfully")
        
        # Process today's scraped content
        logger.info("Starting content processing...")
        results = embedder.process_today_content()
        
        # Print summary
        print_summary(results)
        
        # Determine exit code
        if results['total_documents'] == 0:
            logger.error("No documents were embedded. Check logs for details.")
            return 1
        elif results['failed_embeddings'] > 0:
            logger.warning(
                f"Completed with {results['failed_embeddings']} failures. "
                "Check logs for details."
            )
            return 1
        else:
            logger.info("All documents embedded successfully!")
            return 0
            
    except FileNotFoundError as e:
        logging.error(f"Configuration error: {str(e)}")
        return 1
    except ValueError as e:
        logging.error(f"Configuration validation error: {str(e)}")
        return 1
    except ImportError as e:
        logging.error(f"Missing dependency: {str(e)}")
        return 1
    except KeyboardInterrupt:
        logging.warning("Process interrupted by user")
        return 130
    except Exception as e:
        logging.error(
            f"Fatal error in main execution: {str(e)}",
            exc_info=True
        )
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)