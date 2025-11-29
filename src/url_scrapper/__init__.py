"""
URL Scrapper Package

A production-grade URL content scraping module for tech trend analysis.
"""

from .config_manager import ConfigManager
from .file_processor import FileProcessor
from .models import (
    ProcessingReport,
    ScrapedContent,
    ScrapedOutput,
    Trend,
    TrendAnalysis
)
from .scraper import URLScraper

__version__ = "1.0.0"
__all__ = [
    "ConfigManager",
    "FileProcessor",
    "URLScraper",
    "ProcessingReport",
    "ScrapedContent",
    "ScrapedOutput",
    "Trend",
    "TrendAnalysis",
]