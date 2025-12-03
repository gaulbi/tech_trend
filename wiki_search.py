#!/usr/bin/env python3
"""
Wikipedia Search Module - Main Entry Point

Searches Wikipedia for tech trend keywords, extracts and cleans content,
and stores results for today's date only.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from wiki_search.orchestrator import WikiSearchOrchestrator


def main() -> int:
    """
    Main entry point for Wikipedia search module.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    orchestrator = WikiSearchOrchestrator()
    return orchestrator.run()


if __name__ == "__main__":
    sys.exit(main())