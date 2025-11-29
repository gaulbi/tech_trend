#!/usr/bin/env python3
"""
URL Scraper - Main Entry Point

Processes tech trend analysis files for today's date and scrapes URLs.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from url_scraper.scraper import URLScraper
from url_scraper.exceptions import ConfigurationError


def main() -> int:
    """
    Main entry point for URL scraper.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        scraper = URLScraper()
        scraper.run()
        return 0
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())