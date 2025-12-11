#!/usr/bin/env python3
"""
URL Scraper Entry Point

This script serves as the entry point for the URL scraping module.
All business logic is implemented in the src/url_scraper package.
"""

import sys
from src.url_scraper.main import main

if __name__ == "__main__":
    sys.exit(main())