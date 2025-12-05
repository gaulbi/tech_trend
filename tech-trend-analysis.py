#!/usr/bin/env python3
"""
Tech Trend Analysis - Main Entry Point

This script analyzes RSS feeds to generate daily technology trend reports.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).resolve().parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    from tech_trend_analysis.main import main
except ModuleNotFoundError as e:
    print(f"Error: Cannot import tech_trend_analysis module.", file=sys.stderr)
    print(f"Please ensure the following directory structure exists:", file=sys.stderr)
    print(f"  src/tech_trend_analysis/__init__.py", file=sys.stderr)
    print(f"  src/tech_trend_analysis/main.py", file=sys.stderr)
    print(f"  ... (other module files)", file=sys.stderr)
    print(f"\nOriginal error: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())