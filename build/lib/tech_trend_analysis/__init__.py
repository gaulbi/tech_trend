"""
Tech Trend Analysis Package
============================

This package provides functionality to analyze RSS feeds and generate
technology trend reports using various LLM providers.

Module Structure:
- main.py: Main orchestration logic
- config.py: Configuration loading and validation
- llm/: LLM provider implementations
- models.py: Data models and schemas
- processor.py: RSS feed processing logic
- logger.py: JSON logging utilities
- exceptions.py: Custom exception classes
"""

# src/tech_trend_analysis/__init__.py
__version__ = "1.0.0"
__all__ = ["main"]

from .main import main