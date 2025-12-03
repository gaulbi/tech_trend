#!/usr/bin/env python3
"""
Web Scraper Main Entry Point

This module orchestrates the web scraping process for tech trend analysis.
It processes input files for today's date only and stores cleaned content.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.web_scraper.orchestrator import ScraperOrchestrator
from src.web_scraper.exceptions import ConfigurationError


def main() -> int:
    """
    Main entry point for the web scraper.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        orchestrator = ScraperOrchestrator()
        orchestrator.run()
        return 0
    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())