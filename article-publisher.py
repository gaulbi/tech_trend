#!/usr/bin/env python3
"""
Article Publisher - Main Entry Point
Publishes technology articles to Hashnode using GraphQL API
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from article_publisher.cli import main

if __name__ == "__main__":
    main()
